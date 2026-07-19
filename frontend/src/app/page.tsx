"use client";

import { useCallback, useEffect, useState } from "react";
import { AssetCard } from "@/components/AssetCard";
import { AuditLogPanel } from "@/components/AuditLogPanel";
import { DemoIntroBanner } from "@/components/DemoIntroBanner";
import { PipelineVisualizer } from "@/components/PipelineVisualizer";
import { type Asset, fetchAssets, streamGeneration } from "@/lib/api";

type Step = {
  id: string;
  label: string;
  provider: string;
  status: string;
  b2_op?: string | null;
};

const DEMO_BRIEF =
  "Spanish-market product launch video, 30 seconds, professional tone, includes voiceover and music bed.";

export default function ConsolePage() {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [brief, setBrief] = useState(DEMO_BRIEF);
  const [generating, setGenerating] = useState(false);
  const [steps, setSteps] = useState<Step[]>([]);
  const [activeIndex, setActiveIndex] = useState(-1);
  const [elapsed, setElapsed] = useState(0);
  const [showPipeline, setShowPipeline] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [auditRefresh, setAuditRefresh] = useState(0);
  const [parentRunId, setParentRunId] = useState<string | null>(null);
  const [reviseLabel, setReviseLabel] = useState<string | null>(null);

  const [apiOffline, setApiOffline] = useState(false);

  const loadAssets = useCallback(async () => {
    try {
      const data = await fetchAssets();
      setAssets(data);
      setApiOffline(false);
    } catch {
      setApiOffline(true);
    }
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- async fetch-on-mount; state updates occur after await
    loadAssets();
    // Retry while the backend boots so the banner clears without a manual reload
    const id = setInterval(loadAssets, 5000);
    return () => clearInterval(id);
  }, [loadAssets]);

  useEffect(() => {
    if (!generating) return;
    const t0 = Date.now();
    const id = setInterval(() => setElapsed((Date.now() - t0) / 1000), 100);
    return () => clearInterval(id);
  }, [generating]);

  const handleRevise = (asset: Asset) => {
    if (!asset.run_id) return;
    setParentRunId(asset.run_id);
    setReviseLabel(asset.run_id.slice(0, 8));
    setBrief(asset.brief);
  };

  const clearRevise = () => {
    setParentRunId(null);
    setReviseLabel(null);
  };

  const handleGenerate = () => {
    setError(null);
    setGenerating(true);
    setShowPipeline(true);
    setSteps([]);
    setActiveIndex(-1);
    setElapsed(0);

    streamGeneration(
      brief,
      parentRunId ? "Revision" : "Product launch video",
      (event) => {
        if (event.type === "step" && event.step) {
          const step = event.step as Step;
          setSteps((prev) => {
            const runningIdx = prev.findIndex((s) => s.id === step.id && s.status === "running");
            if (runningIdx >= 0) {
              const next = [...prev];
              next[runningIdx] = step;
              return next;
            }
            return [...prev, step];
          });
          if (step.status === "running") {
            setActiveIndex((prev) => prev + 1);
          }
        }
        if (event.type === "complete") {
          setGenerating(false);
          loadAssets();
          setAuditRefresh((k) => k + 1);
          clearRevise();
        }
        if (event.type === "error") {
          setGenerating(false);
          setError(String(event.message ?? "Generation failed"));
        }
      },
      parentRunId,
    );
  };

  return (
    <div className="mx-auto max-w-6xl px-8 py-10">
      <header className="mb-10">
        <p className="label-caps text-muted">Compliance Console</p>
        <h1 className="font-display mt-2 text-[2rem] font-light leading-tight tracking-[-0.02em] text-ink">
          EU Fintech — Media Compliance
        </h1>
        <p className="mt-3 max-w-2xl text-sm leading-relaxed text-muted">
          Every AI-generated asset ships with Ed25519 signature, C2PA-candidate manifest, invisible
          watermark, and tamper-evident audit trail in Backblaze B2.
        </p>
      </header>

      <DemoIntroBanner />

      {apiOffline && (
        <div className="mb-8 flex items-center gap-3 rounded-[var(--radius-md)] border border-danger/40 bg-danger/[0.06] px-4 py-3">
          <span className="h-2 w-2 shrink-0 animate-pulse rounded-full bg-danger" />
          <p className="text-sm text-danger">
            API unreachable — start the backend (<span className="font-mono text-[12px]">uvicorn attest.main:app --port 8000</span>). Retrying…
          </p>
        </div>
      )}

      <section className="card mb-8 p-6">
        <h2 className="font-display mb-4 text-base font-medium text-ink">New generation</h2>
        {reviseLabel && (
          <p className="mb-3 rounded-[var(--radius-sm)] border border-warning/30 bg-warning/8 px-3 py-2 font-mono text-xs text-warning">
            Revising — parent_run_id: {reviseLabel}…{" "}
            <button type="button" onClick={clearRevise} className="underline hover:text-warning/80">
              Cancel
            </button>
          </p>
        )}
        <textarea
          value={brief}
          onChange={(e) => setBrief(e.target.value)}
          rows={3}
          disabled={generating}
          className="input-field mb-4 resize-none disabled:opacity-50"
          placeholder="Describe the asset to generate…"
        />
        {error && <p className="mb-3 text-sm text-danger">{error}</p>}
        <button
          onClick={handleGenerate}
          disabled={generating || brief.length < 10}
          className="btn-primary"
        >
          {generating ? "Generating…" : "Generate"}
        </button>
      </section>

      {showPipeline && (
        <section className="card mb-8 p-6">
          <PipelineVisualizer
            steps={steps}
            activeIndex={activeIndex >= 0 ? activeIndex : steps.length - 1}
            elapsed={elapsed}
          />
        </section>
      )}

      <div className="grid gap-8 lg:grid-cols-[1fr_300px]">
        <section>
          <h2 className="font-display mb-4 text-base font-medium text-ink">Assets</h2>
          {assets.length === 0 ? (
            <p className="rounded-[var(--radius-lg)] border border-dashed border-border py-14 text-center text-sm text-muted">
              No assets yet. Start the backend and click Generate.
            </p>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2">
              {assets.map((a) => (
                <AssetCard key={a.id} asset={a} onRevise={handleRevise} />
              ))}
            </div>
          )}
        </section>
        <AuditLogPanel refreshKey={auditRefresh} />
      </div>
    </div>
  );
}
