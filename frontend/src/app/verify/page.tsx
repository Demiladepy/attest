"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { LineageTree } from "@/components/LineageTree";
import { tamperAsset, verifyAsset, type VerificationResult } from "@/lib/api";

function CheckIcon({ status }: { status: string }) {
  if (status === "pass") return <span className="text-success">✓</span>;
  if (status === "fail") return <span className="text-danger">✗</span>;
  if (status === "warn") return <span className="text-warning">!</span>;
  return <span className="text-muted">–</span>;
}

function VerifyForm() {
  const searchParams = useSearchParams();
  const [url, setUrl] = useState("");
  const [manifestUrl, setManifestUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<VerificationResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [tampering, setTampering] = useState(false);

  useEffect(() => {
    const asset = searchParams.get("asset");
    const manifest = searchParams.get("manifest");
    if (asset) {
      setUrl(asset);
      if (manifest) setManifestUrl(manifest);
    }
  }, [searchParams]);

  const handleVerify = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await verifyAsset(url, manifestUrl || undefined);
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Verification failed");
    } finally {
      setLoading(false);
    }
  };

  const handleTamper = async () => {
    if (!url.trim()) return;
    setTampering(true);
    setError(null);
    try {
      const t = await tamperAsset(url, undefined, result?.manifest?.run_id ?? undefined);
      setUrl(t.tampered_url);
      setLoading(true);
      const data = await verifyAsset(t.tampered_url, manifestUrl || undefined);
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Tamper simulation failed");
    } finally {
      setTampering(false);
      setLoading(false);
    }
  };

  useEffect(() => {
    const asset = searchParams.get("asset");
    if (!asset) return;
    handleVerify();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams.get("asset")]);

  const overallClass =
    result?.overall === "pass"
      ? "border-success/40 bg-success/[0.04]"
      : result?.overall === "fail"
        ? "border-danger/40 bg-danger/[0.04]"
        : "border-warning/40 bg-warning/[0.04]";

  return (
    <>
      <div className="card mb-8 p-6">
        <label className="label-caps mb-2 block text-muted">Asset URL</label>
        <input
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="http://localhost:8000/assets/…/output.png"
          className="input-field mb-4 font-mono text-[13px]"
        />
        <label className="label-caps mb-2 block text-muted">Manifest URL (optional)</label>
        <input
          type="url"
          value={manifestUrl}
          onChange={(e) => setManifestUrl(e.target.value)}
          placeholder="http://localhost:8000/assets/…/manifest.json"
          className="input-field mb-4 font-mono text-[13px]"
        />
        {error && <p className="mb-3 text-sm text-danger">{error}</p>}
        <button
          onClick={handleVerify}
          disabled={loading || !url.trim()}
          className="btn-primary w-full py-3"
        >
          {loading ? "Verifying…" : "Verify"}
        </button>
        {result?.overall === "pass" && !url.includes("-tampered") && (
          <button
            type="button"
            onClick={handleTamper}
            disabled={tampering || loading}
            className="btn-danger-ghost mt-3 w-full"
          >
            {tampering ? "Re-encoding…" : "Simulate tamper (re-encode)"}
          </button>
        )}
      </div>

      {result && (
        <div className={`rounded-[var(--radius-lg)] border p-6 ${overallClass}`}>
          <div className="mb-6 flex items-center justify-between">
            <h2 className="font-display text-lg font-semibold">
              {result.overall === "pass" ? "Verified" : result.overall === "fail" ? "Failed" : "Partial"}
            </h2>
            <span className="label-caps font-mono text-muted">{result.overall}</span>
          </div>

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

          <LineageTree nodes={result.lineage} />
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
        <h1 className="font-display mt-2 text-[1.75rem] font-semibold tracking-tight text-ink">
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
