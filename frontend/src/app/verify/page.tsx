"use client";

import { useState } from "react";
import { verifyAsset, type VerificationResult } from "@/lib/api";

function CheckIcon({ status }: { status: string }) {
  if (status === "pass") return <span className="text-emerald-400">✓</span>;
  if (status === "fail") return <span className="text-red-400">✗</span>;
  if (status === "warn") return <span className="text-amber-400">!</span>;
  return <span className="text-zinc-500">–</span>;
}

export default function VerifyPage() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<VerificationResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleVerify = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await verifyAsset(url);
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Verification failed");
    } finally {
      setLoading(false);
    }
  };

  const overallColor =
    result?.overall === "pass"
      ? "border-emerald-500/50 bg-emerald-500/5"
      : result?.overall === "fail"
        ? "border-red-500/50 bg-red-500/5"
        : "border-amber-500/50 bg-amber-500/5";

  return (
    <div className="mx-auto max-w-3xl px-6 py-10">
      <div className="mb-10 text-center">
        <p className="mb-1 text-sm text-zinc-500">Public Verifier</p>
        <h1 className="text-3xl font-semibold tracking-tight">verify.attest.io</h1>
        <p className="mt-2 text-zinc-400">
          Paste a B2 durable URL. Verify signature, C2PA claim, watermark, and lineage.
        </p>
      </div>

      <div className="mb-8 rounded-2xl border border-zinc-800 bg-zinc-900/40 p-6">
        <label className="mb-2 block text-sm font-medium text-zinc-300">Asset URL</label>
        <input
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://f004.backblazeb2.com/file/…/output.mp4"
          className="mb-4 w-full rounded-xl border border-zinc-700 bg-zinc-950 px-4 py-3 font-mono text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
        {error && <p className="mb-3 text-sm text-red-400">{error}</p>}
        <button
          onClick={handleVerify}
          disabled={loading || !url.trim()}
          className="w-full rounded-xl bg-indigo-600 py-3 text-sm font-medium text-white transition hover:bg-indigo-500 disabled:opacity-40"
        >
          {loading ? "Verifying…" : "Verify"}
        </button>
      </div>

      {result && (
        <div className={`rounded-2xl border p-6 ${overallColor}`}>
          <div className="mb-6 flex items-center justify-between">
            <h2 className="text-lg font-medium">
              {result.overall === "pass" ? "Verified" : result.overall === "fail" ? "Failed" : "Partial"}
            </h2>
            <span className="font-mono text-xs text-zinc-500 uppercase">{result.overall}</span>
          </div>

          <div className="space-y-3">
            {result.checks.map((check) => (
              <div
                key={check.id}
                className="flex items-start gap-3 rounded-lg border border-zinc-800/80 bg-zinc-950/50 px-4 py-3"
              >
                <CheckIcon status={check.status} />
                <div>
                  <p className="text-sm font-medium text-zinc-200">{check.label}</p>
                  {check.detail && <p className="text-xs text-zinc-500">{check.detail}</p>}
                </div>
              </div>
            ))}
          </div>

          {result.lineage.length > 0 && (
            <div className="mt-8">
              <h3 className="mb-3 text-sm font-semibold uppercase tracking-wider text-zinc-500">
                Lineage (parent_run_id)
              </h3>
              <div className="space-y-2 border-l-2 border-indigo-500/30 pl-4">
                {result.lineage.map((node, i) => (
                  <div key={i} className="text-sm">
                    <span className="font-mono text-indigo-400">{node.run_id.slice(0, 8)}…</span>
                    <span className="mx-2 text-zinc-600">→</span>
                    <span className="text-zinc-400">{node.status}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
