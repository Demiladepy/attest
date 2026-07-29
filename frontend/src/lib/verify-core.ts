// Server-side verification (runs as a Node serverless function on Vercel).
// Faithful port of backend/attest/compliance/verify.py — re-hashes the manifest
// with the same canonical JSON the Python signer uses, so the hash matches
// byte-for-byte, and verifies the Ed25519 signature with Node crypto.

import crypto from "node:crypto";

// Public verification key (safe to embed — it is published in attest-pubkey.pem).
const TRUSTED_KEY = (process.env.ATTEST_VERIFY_KEY_HEX ?? "").trim() ||
  "cd09bb50779be236fa5a01e2ffde6f191827554a87a70e9a2c898870800421a5";

type Check = { id: string; label: string; status: "pass" | "fail" | "warn"; detail: string };
type Manifest = Record<string, unknown>;

// Reproduce Python json.dumps(sort_keys=True, separators=(",",":"), ensure_ascii=True)
function canon(v: unknown): string {
  if (v === null) return "null";
  if (typeof v === "number") return Number.isInteger(v) ? String(v) : JSON.stringify(v);
  if (typeof v === "boolean") return v ? "true" : "false";
  if (typeof v === "string") return escStr(v);
  if (Array.isArray(v)) return "[" + v.map(canon).join(",") + "]";
  const o = v as Record<string, unknown>;
  return "{" + Object.keys(o).sort().map((k) => escStr(k) + ":" + canon(o[k])).join(",") + "}";
}

function escStr(s: string): string {
  let out = '"';
  for (const ch of s) {
    const c = ch.codePointAt(0)!;
    if (ch === '"') out += '\\"';
    else if (ch === "\\") out += "\\\\";
    else if (c === 0x08) out += "\\b";
    else if (c === 0x09) out += "\\t";
    else if (c === 0x0a) out += "\\n";
    else if (c === 0x0c) out += "\\f";
    else if (c === 0x0d) out += "\\r";
    else if (c < 0x20) out += "\\u" + c.toString(16).padStart(4, "0");
    else if (c > 0x7e) {
      if (c > 0xffff) {
        const h = Math.floor((c - 0x10000) / 0x400) + 0xd800;
        const l = ((c - 0x10000) % 0x400) + 0xdc00;
        out += "\\u" + h.toString(16).padStart(4, "0") + "\\u" + l.toString(16).padStart(4, "0");
      } else out += "\\u" + c.toString(16).padStart(4, "0");
    } else out += ch;
  }
  return out + '"';
}

function sha256hex(buf: Buffer): string {
  return crypto.createHash("sha256").update(buf).digest("hex");
}

// Verify an Ed25519 signature (raw 32-byte pubkey hex) over a UTF-8 message.
function ed25519Verify(pubHex: string, message: string, sigB64: string): boolean {
  const der = Buffer.concat([
    Buffer.from("302a300506032b6570032100", "hex"), // SPKI header for Ed25519
    Buffer.from(pubHex, "hex"),
  ]);
  const key = crypto.createPublicKey({ key: der, format: "der", type: "spki" });
  return crypto.verify(null, Buffer.from(message, "utf8"), key, Buffer.from(sigB64, "base64"));
}

function overall(checks: Check[]): "pass" | "fail" | "warn" {
  if (checks.some((c) => c.status === "fail")) return "fail";
  if (checks.some((c) => c.status === "warn")) return "warn";
  return "pass";
}

export async function verifyAssetUrl(
  assetUrl: string,
  manifestUrl?: string,
  expectedSha256?: string,
) {
  const checks: Check[] = [];
  let manifest: Manifest | null = null;
  const lineage: Array<Record<string, unknown>> = [];

  // 1. Asset reachable + hash
  let actualSha: string;
  try {
    const r = await fetch(assetUrl, { redirect: "follow" });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    actualSha = sha256hex(Buffer.from(await r.arrayBuffer()));
    checks.push({ id: "asset_fetch", label: "Asset reachable", status: "pass", detail: `sha256:${actualSha.slice(0, 16)}…` });
  } catch (e) {
    checks.push({ id: "asset_fetch", label: "Asset reachable", status: "fail", detail: String(e) });
    return { asset_url: assetUrl, overall: "fail", checks, lineage: [], manifest: null };
  }

  // 2. Manifest
  let resolved = manifestUrl;
  if (!resolved && /\.(png|jpe?g|webp)$/i.test(assetUrl)) {
    resolved = assetUrl.replace(/\/[^/]+$/, "/manifest.json");
  }
  if (resolved) {
    try {
      const r = await fetch(resolved, { redirect: "follow" });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      manifest = (await r.json()) as Manifest;
      checks.push({ id: "manifest_parse", label: "Manifest parsed", status: "pass", detail: "" });
    } catch (e) {
      checks.push({ id: "manifest_parse", label: "Manifest parsed", status: "fail", detail: String(e) });
    }
  } else {
    checks.push({ id: "manifest_parse", label: "Manifest parsed", status: "warn", detail: "No manifest URL provided" });
  }

  // 3. SHA-256 integrity
  let manifestSha: string | undefined;
  if (manifest) {
    const outs = (manifest.outputs as Array<Record<string, string>>) ?? (manifest.assets as Array<Record<string, string>>) ?? [];
    manifestSha = outs[0]?.sha256 ?? outs[0]?.hash ?? (manifest.sha256 as string | undefined);
  }
  const expected = (expectedSha256 ?? manifestSha ?? "").toLowerCase();
  if (expected) {
    const ok = actualSha.toLowerCase() === expected;
    checks.push({ id: "sha256", label: "SHA-256 integrity", status: ok ? "pass" : "fail",
      detail: ok ? "" : `expected ${expected.slice(0, 16)}… got ${actualSha.slice(0, 16)}…` });
  } else {
    checks.push({ id: "sha256", label: "SHA-256 integrity", status: "warn", detail: "No reference hash in manifest" });
  }

  // 4–7. Signature, C2PA, watermark, lineage
  if (manifest) {
    const attest = (manifest.attest as Record<string, unknown>) ?? {};
    const sig = attest.signature as Record<string, string> | undefined;
    if (sig) {
      try {
        const core: Manifest = { ...manifest };
        delete core.attest;
        const canonicalOk = sha256hex(Buffer.from(canon(core), "utf8")) === sig.manifest_sha256;
        const sigOk = ed25519Verify(sig.public_key_hex, sig.manifest_sha256, sig.signature_b64);
        const trustedOk = !TRUSTED_KEY || sig.public_key_hex === TRUSTED_KEY;
        const ok = canonicalOk && sigOk && trustedOk;
        const detail = ok ? "" : !canonicalOk ? "Manifest changed since signing"
          : !trustedOk ? "Public key not trusted by ATTEST" : "Signature invalid";
        checks.push({ id: "ed25519", label: "Ed25519 signature", status: ok ? "pass" : "fail", detail });
      } catch (e) {
        checks.push({ id: "ed25519", label: "Ed25519 signature", status: "fail", detail: String(e) });
      }
    } else {
      checks.push({ id: "ed25519", label: "Ed25519 signature", status: "warn", detail: "No signature block in manifest" });
    }

    const c2pa = (attest.c2pa as Record<string, unknown>) ?? {};
    checks.push(c2pa.embedded
      ? { id: "c2pa", label: "C2PA claim", status: c2pa.valid === false ? "fail" : "pass", detail: String(c2pa.detail ?? "Embedded in asset") }
      : { id: "c2pa", label: "C2PA claim", status: "warn", detail: "Not embedded (roadmap: Mode 3)" });

    const wm = (attest.watermark as Record<string, unknown>) ?? {};
    if (wm.detected) {
      const score = Number(wm.confidence ?? 1);
      checks.push({ id: "watermark", label: "Invisible watermark", status: score >= 0.5 ? "pass" : "fail", detail: `confidence=${score.toFixed(2)}` });
    } else {
      checks.push({ id: "watermark", label: "Invisible watermark", status: "warn", detail: String(wm.detail ?? "Not detected or not applicable") });
    }

    for (const [i, anc] of ((attest.lineage as Array<Record<string, unknown>>) ?? []).entries()) {
      lineage.push({ run_id: anc.run_id ?? "", parent_run_id: anc.parent_run_id ?? null, status: anc.status ?? "rejected", created_at: anc.created_at ?? "", depth: i });
    }
    lineage.push({ run_id: manifest.run_id ?? "", parent_run_id: manifest.parent_run_id ?? null, status: "approved", created_at: manifest.created_at ?? "", depth: lineage.length });
  }

  return { asset_url: assetUrl, overall: overall(checks), checks, lineage, manifest };
}
