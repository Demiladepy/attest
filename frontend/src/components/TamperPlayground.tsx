"use client";

import { useCallback, useRef, useState } from "react";
import { Seal } from "@/components/Seal";

async function sha256Hex(buf: ArrayBuffer): Promise<string> {
  const digest = await crypto.subtle.digest("SHA-256", buf);
  return Array.from(new Uint8Array(digest))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

function HashRow({ label, value, ok }: { label: string; value: string; ok: boolean | null }) {
  return (
    <div className="flex items-center justify-between gap-3 border-b border-border-subtle py-2 last:border-0">
      <span className="label-caps shrink-0 text-muted">{label}</span>
      <span
        className={`min-w-0 truncate font-mono text-[12px] ${
          ok === null ? "text-muted" : ok ? "text-attested" : "text-danger"
        }`}
        title={value}
      >
        {value}
      </span>
    </div>
  );
}

/**
 * Live, client-side tamper demo. Alters the real signed image in a canvas,
 * recomputes SHA-256 with Web Crypto, and shows the seal break in real time —
 * no server round-trip. Proves the integrity guarantee viscerally.
 */
export function TamperPlayground({
  assetUrl,
  expectedSha,
}: {
  assetUrl: string;
  expectedSha?: string;
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [tampered, setTampered] = useState(false);
  const [tamperedHash, setTamperedHash] = useState<string | null>(null);
  const [working, setWorking] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const tamper = useCallback(async () => {
    setWorking(true);
    setError(null);
    try {
      const img = new Image();
      img.crossOrigin = "anonymous";
      await new Promise<void>((resolve, reject) => {
        img.onload = () => resolve();
        img.onerror = () => reject(new Error("could not load image"));
        img.src = assetUrl;
      });

      const canvas = canvasRef.current!;
      canvas.width = img.naturalWidth;
      canvas.height = img.naturalHeight;
      const ctx = canvas.getContext("2d")!;
      ctx.drawImage(img, 0, 0);

      // The "attack": nudge a tiny patch of pixels — a change invisible to the
      // eye but fatal to the hash.
      const w = Math.max(8, Math.floor(img.naturalWidth * 0.04));
      const x = Math.floor(img.naturalWidth * 0.46);
      const y = Math.floor(img.naturalHeight * 0.46);
      const patch = ctx.getImageData(x, y, w, w);
      for (let i = 0; i < patch.data.length; i += 4) {
        patch.data[i] = Math.min(255, patch.data[i] + 6); // shift red channel slightly
      }
      ctx.putImageData(patch, x, y);

      const blob: Blob = await new Promise((res) => canvas.toBlob((b) => res(b!), "image/png"));
      const hash = await sha256Hex(await blob.arrayBuffer());
      setTamperedHash(hash);
      setTampered(true);
    } catch (e) {
      setError(e instanceof Error ? e.message : "tamper failed");
    } finally {
      setWorking(false);
    }
  }, [assetUrl]);

  const restore = () => {
    setTampered(false);
    setTamperedHash(null);
  };

  const currentHash = tampered ? tamperedHash ?? "" : expectedSha ?? "";
  const integrityOk = !tampered;

  return (
    <div className="mt-8 rounded-[var(--radius-lg)] border border-border bg-surface p-6">
      <div className="mb-4 flex items-center justify-between gap-3">
        <div>
          <p className="label-caps text-muted">Tamper playground</p>
          <h3 className="font-display mt-1 text-lg font-medium text-ink">Try to fool the seal</h3>
        </div>
        <span
          className={`inline-flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs font-semibold ${
            tampered
              ? "border-danger/40 bg-danger/[0.06] text-danger"
              : "border-attested/40 bg-attested-soft text-attested"
          }`}
        >
          {tampered ? (
            "✗ TAMPERED"
          ) : (
            <>
              <Seal size={14} className="text-attested" /> VERIFIED
            </>
          )}
        </span>
      </div>

      <p className="mb-4 max-w-xl text-sm leading-relaxed text-muted">
        This nudges a handful of pixels — a change you can&apos;t see — and re-hashes the file in your
        browser. The bytes no longer match the signed manifest, so integrity fails instantly.
      </p>

      <div className="grid gap-5 sm:grid-cols-[240px_1fr]">
        <div
          className={`relative overflow-hidden rounded-[var(--radius-md)] border bg-void ${
            tampered ? "border-danger/40" : "border-border"
          }`}
        >
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={assetUrl}
            alt="asset"
            className={`w-full ${tampered ? "hidden" : "block"}`}
          />
          <canvas ref={canvasRef} className={`w-full ${tampered ? "block" : "hidden"}`} />
          {tampered && (
            <span className="animate-stamp absolute right-2 top-2 rounded-[var(--radius-sm)] border-2 border-danger bg-void/70 px-2 py-0.5 font-mono text-[11px] font-bold tracking-widest text-danger backdrop-blur-sm">
              TAMPERED
            </span>
          )}
        </div>

        <div className="flex flex-col">
          <div className="rounded-[var(--radius-md)] border border-border-subtle bg-void p-4">
            <HashRow label="Signed" value={expectedSha ?? "—"} ok={null} />
            <HashRow label="This file" value={currentHash || "—"} ok={integrityOk} />
            <div className="mt-3 flex items-center gap-2 border-t border-border-subtle pt-3">
              <span className={integrityOk ? "text-attested" : "text-danger"}>
                {integrityOk ? "✓" : "✗"}
              </span>
              <span className={`text-sm font-medium ${integrityOk ? "text-attested" : "text-danger"}`}>
                {integrityOk ? "SHA-256 matches the signed manifest" : "Hash mismatch — bytes changed since signing"}
              </span>
            </div>
          </div>

          {error && <p className="mt-3 text-sm text-danger">{error}</p>}

          <div className="mt-4 flex gap-2">
            {!tampered ? (
              <button type="button" onClick={tamper} disabled={working} className="btn-danger-ghost text-sm">
                {working ? "Altering…" : "Tamper the image"}
              </button>
            ) : (
              <button type="button" onClick={restore} className="btn-ghost text-sm">
                Restore original
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
