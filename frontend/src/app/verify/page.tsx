"use client";

import { Suspense, useCallback, useEffect, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import { LineageTree } from "@/components/LineageTree";
import { Seal } from "@/components/Seal";
import { TamperPlayground } from "@/components/TamperPlayground";
import { verifyAsset, type VerificationResult } from "@/lib/api";

function CheckIcon({ status }: { status: string }) {
  if (status === "pass") return <span className="text-success">✓</span>;
  if (status === "fail") return <span className="text-danger">✗</span>;
  if (status === "warn") return <span className="text-warning">!</span>;
  return <span className="text-muted">–</span>;
}

const VERDICT = {
  pass: {
    title: "Verified",
    sub: "Signature, integrity, and provenance checks passed. This asset is exactly what its manifest attests.",
    stamp: "VERIFIED",
    stampClass: "border-success text-success",
    frame: "border-success/40 bg-success/[0.04]",
    halo: "bg-success/10 text-success border-success/40",
  },
  fail: {
    title: "Tamper detected",
    sub: "This asset does not match its signed manifest. Its bytes were modified after signing.",
    stamp: "TAMPERED",
    stampClass: "border-danger text-danger",
    frame: "border-danger/40 bg-danger/[0.04]",
    halo: "bg-danger/10 text-danger border-danger/40",
  },
  warn: {
    title: "Partial verification",
    sub: "Core checks passed but some provenance data is missing or unverifiable.",
    stamp: "PARTIAL",
    stampClass: "border-warning text-warning",
    frame: "border-warning/40 bg-warning/[0.04]",
    halo: "bg-warning/10 text-warning border-warning/40",
  },
} as const;

function ProvenanceRow({ label, value, mono = true }: { label: string; value: string; mono?: boolean }) {
  return (
    <div className="flex items-baseline justify-between gap-4 border-b border-border-subtle py-2 last:border-0">
      <span className="label-caps shrink-0 text-muted">{label}</span>
      <span className={`min-w-0 break-all text-right text-[12px] text-ink ${mono ? "font-mono" : ""}`}>
        {value}
      </span>
    </div>
  );
}

function VerifyForm() {
  const searchParams = useSearchParams();
  const [url, setUrl] = useState("");
  const [manifestUrl, setManifestUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<VerificationResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [imgOk, setImgOk] = useState(true);
  const [copied, setCopied] = useState(false);
  const autoRan = useRef(false);

  const runVerify = useCallback(async (assetUrl: string, manifest?: string) => {
    if (!assetUrl.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    setImgOk(true);
    try {
      const data = await verifyAsset(assetUrl, manifest || undefined);
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Verification failed");
    } finally {
      setLoading(false);
    }
  }, []);

  // Deep link: read params once, seed the form, and verify with the param
  // values directly (never via state — state is not yet set on first render).
  useEffect(() => {
    const asset = searchParams.get("asset");
    if (!asset || autoRan.current) return;
    autoRan.current = true;
    const manifest = searchParams.get("manifest") ?? "";
    setUrl(asset);
    setManifestUrl(manifest);
    runVerify(asset, manifest);
  }, [searchParams, runVerify]);

  const runDemo = (kind: "signed" | "tampered") => {
    const origin = window.location.origin;
    const file = kind === "signed" ? "output.png" : "output-tampered.png";
    const asset = `${origin}/demo/${file}`;
    const manifest = `${origin}/demo/manifest.json`;
    setUrl(asset);
    setManifestUrl(manifest);
    runVerify(asset, manifest);
  };

  const handleCopyLink = async () => {
    const link = `${window.location.origin}/verify?asset=${encodeURIComponent(url)}${
      manifestUrl ? `&manifest=${encodeURIComponent(manifestUrl)}` : ""
    }`;
    try {
      await navigator.clipboard.writeText(link);
      setCopied(true);
      setTimeout(() => setCopied(false), 1600);
    } catch {
      /* clipboard unavailable */
    }
  };

  const verdict = result ? VERDICT[result.overall] : null;
  const manifest = result?.manifest;
  const sig = manifest?.attest?.signature;
  const output = manifest?.outputs?.[0];
  const lock = manifest?.attest?.object_lock;
  const isImage =
    /\.(png|jpe?g|webp|gif)(\?|$)/i.test(result?.asset_url ?? "") ||
    (output?.mime ?? "").startsWith("image/");

  return (
    <>
      <div className="card no-print mb-4 p-4">
        <p className="label-caps mb-3 text-muted">Try it — one click</p>
        <div className="flex flex-wrap gap-2">
          <button type="button" onClick={() => runDemo("signed")} disabled={loading} className="btn-primary text-sm">
            Verify a signed asset
          </button>
          <button type="button" onClick={() => runDemo("tampered")} disabled={loading} className="btn-danger-ghost text-sm">
            Verify a tampered copy
          </button>
        </div>
        <p className="mt-3 text-xs leading-relaxed text-muted">
          A real Ed25519-signed image vs. the same image with one re-encode. Same manifest — the hash
          check catches the tampered bytes.
        </p>
      </div>

      <div className="card no-print mb-8 p-6">
        <label className="label-caps mb-2 block text-muted">Asset URL</label>
        <input
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://api…/api/storage/…/output.png"
          className="input-field mb-4 font-mono text-[13px]"
        />
        <label className="label-caps mb-2 block text-muted">Manifest URL (optional)</label>
        <input
          type="url"
          value={manifestUrl}
          onChange={(e) => setManifestUrl(e.target.value)}
          placeholder="https://api…/api/storage/…/manifest.json"
          className="input-field mb-4 font-mono text-[13px]"
        />
        {error && <p className="mb-3 text-sm text-danger">{error}</p>}
        <button
          onClick={() => runVerify(url, manifestUrl)}
          disabled={loading || !url.trim()}
          className="btn-primary w-full py-3"
        >
          {loading ? "Verifying…" : "Verify"}
        </button>
      </div>

      {result && verdict && (
        <div className={`print-cert animate-fade-up rounded-[var(--radius-lg)] border p-6 ${verdict.frame}`}>
          {/* Print-only certificate header */}
          <div className="mb-6 hidden items-center justify-between border-b border-border pb-4 print:flex">
            <div className="flex items-center gap-2.5">
              <Seal size={30} className="text-ink" />
              <span className="font-display text-lg font-semibold tracking-tight text-ink">ATTEST</span>
            </div>
            <span className="font-mono text-[11px] text-muted">
              Issued {new Date().toUTCString()}
            </span>
          </div>

          {/* Verdict banner */}
          <div className="mb-6 flex items-start justify-between gap-4">
            <div>
              {result.overall === "pass" && (
                <p className="label-caps mb-3 text-attested">Certificate of Provenance</p>
              )}
              <div className="flex items-center gap-3">
                {result.overall === "pass" ? (
                  <Seal size={40} animated className="text-attested" />
                ) : (
                  <span
                    className={`inline-flex h-9 w-9 items-center justify-center rounded-full border text-lg font-bold ${verdict.halo}`}
                  >
                    {result.overall === "fail" ? "✗" : "!"}
                  </span>
                )}
                <h2 className="font-display text-2xl font-medium tracking-[-0.02em]">
                  {verdict.title}
                </h2>
              </div>
              <p className="mt-2 max-w-lg text-sm leading-relaxed text-muted">{verdict.sub}</p>
            </div>
            <div className="no-print flex shrink-0 gap-2">
              {result.overall === "pass" && (
                <button
                  type="button"
                  onClick={() => window.print()}
                  className="btn-primary px-3 py-1.5 text-xs"
                >
                  Download certificate
                </button>
              )}
              <button
                type="button"
                onClick={handleCopyLink}
                className="btn-ghost px-3 py-1.5 text-xs"
              >
                {copied ? "Copied ✓" : "Copy link"}
              </button>
            </div>
          </div>

          {/* Asset preview with stamp */}
          {isImage && imgOk && (
            <div className="relative mb-6 overflow-hidden rounded-[var(--radius-md)] border border-border bg-void">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={result.asset_url}
                alt="Verified asset"
                className={`max-h-[420px] w-full object-contain ${
                  result.overall === "fail" ? "opacity-60 saturate-50" : ""
                }`}
                onError={() => setImgOk(false)}
              />
              <span
                className={`pointer-events-none absolute right-4 top-4 -rotate-6 rounded-[var(--radius-sm)] border-2 bg-void/70 px-3 py-1 font-mono text-sm font-bold tracking-[0.2em] backdrop-blur-sm ${verdict.stampClass}`}
              >
                {verdict.stamp}
              </span>
            </div>
          )}

          {/* Checks */}
          <div className="space-y-2">
            {result.checks.map((check) => (
              <div
                key={check.id}
                className="flex items-start gap-3 rounded-[var(--radius-md)] border border-border-subtle bg-void px-4 py-3"
              >
                <CheckIcon status={check.status} />
                <div>
                  <p className="text-sm font-medium text-ink">{check.label}</p>
                  {check.detail && (
                    <p className="mt-0.5 font-mono text-[11px] text-muted">{check.detail}</p>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Provenance card */}
          {manifest && (
            <div className="mt-6 rounded-[var(--radius-md)] border border-border-subtle bg-void p-4">
              <p className="label-caps mb-2 text-muted">Provenance record</p>
              {manifest.run_id && <ProvenanceRow label="Run" value={manifest.run_id} />}
              {manifest.pipeline && <ProvenanceRow label="Pipeline" value={manifest.pipeline} />}
              {manifest.created_at && (
                <ProvenanceRow label="Generated" value={new Date(manifest.created_at).toUTCString()} />
              )}
              {output?.provider && <ProvenanceRow label="Provider" value={output.provider} />}
              {manifest.classification?.model && (
                <ProvenanceRow label="Classifier" value={manifest.classification.model} />
              )}
              {sig?.public_key_hex && (
                <ProvenanceRow label="Signer key" value={`ed25519:${sig.public_key_hex.slice(0, 16)}…`} />
              )}
              {sig?.signed_at && (
                <ProvenanceRow label="Signed" value={new Date(sig.signed_at).toUTCString()} />
              )}
              {manifest.attest?.watermark?.detected && (
                <ProvenanceRow
                  label="Watermark"
                  value={`detected · ${(manifest.attest.watermark.confidence ?? 0).toFixed(2)} confidence`}
                />
              )}
              {lock?.mode && (
                <ProvenanceRow
                  label="B2 Object Lock"
                  value={`${lock.mode}${lock.retain_days ? ` · ${lock.retain_days}d retention` : ""}`}
                />
              )}
              {manifest.classification?.summary && (
                <p className="mt-3 border-t border-border-subtle pt-3 text-[12px] leading-relaxed text-muted">
                  {manifest.classification.summary}
                </p>
              )}
            </div>
          )}

          <LineageTree nodes={result.lineage} />
        </div>
      )}

      {result?.overall === "pass" && isImage && imgOk && (
        <div className="no-print">
          <TamperPlayground assetUrl={result.asset_url} expectedSha={output?.sha256} />
        </div>
      )}
    </>
  );
}

export default function VerifyPage() {
  return (
    <div className="mx-auto max-w-2xl px-8 py-10">
      <header className="mb-10">
        <p className="label-caps text-muted">Public verifier</p>
        <h1 className="font-display mt-2 text-[2rem] font-light leading-tight tracking-[-0.02em] text-ink">
          verify.attest.io
        </h1>
        <p className="mt-3 text-sm leading-relaxed text-muted">
          Paste an asset URL. Verify Ed25519 signature, SHA-256 integrity, and manifest lineage.
        </p>
      </header>

      <Suspense fallback={<p className="text-center text-muted">Loading…</p>}>
        <VerifyForm />
      </Suspense>
    </div>
  );
}
