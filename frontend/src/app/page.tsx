"use client";

import { useCallback, useEffect, useState } from "react";
import { AssetCard } from "@/components/AssetCard";
import { PipelineVisualizer } from "@/components/PipelineVisualizer";
import {
  type Asset,
  fetchAssets,
  streamGeneration,
} from "@/lib/api";

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

  const loadAssets = useCallback(async () => {
    try {
      const data = await fetchAssets();
      setAssets(data);
    } catch {
      /* API may be offline during first boot */
    }
  }, []);

  useEffect(() => {
    loadAssets();
  }, [loadAssets]);

  useEffect(() => {
    if (!generating) return;
    const t0 = Date.now();
    const id = setInterval(() => setElapsed((Date.now() - t0) / 1000), 100);
    return () => clearInterval(id);
  }, [generating]);

  const handleGenerate = () => {
    setError(null);
    setGenerating(true);
    setShowPipeline(true);
    setSteps([]);
    setActiveIndex(-1);
    setElapsed(0);

    streamGeneration(brief, "Product launch video", (event) => {
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
      }
    });
  };

  return (
    <div className="mx-auto max-w-6xl px-6 py-10">
      <div className="mb-10">
        <p className="mb-1 text-sm text-zinc-500">Compliance Console</p>
        <h1 className="text-3xl font-semibold tracking-tight">EU Fintech — Media Compliance</h1>
        <p className="mt-2 max-w-2xl text-zinc-400">
          Every AI-generated asset ships with C2PA provenance, Ed25519 signature, invisible watermark,
          and tamper-evident audit trail in Backblaze B2.
        </p>
      </div>

      <div className="mb-10 rounded-2xl border border-zinc-800 bg-zinc-900/40 p-6">
        <h2 className="mb-4 text-lg font-medium">New Generation</h2>
        <textarea
          value={brief}
          onChange={(e) => setBrief(e.target.value)}
          rows={3}
          disabled={generating}
          className="mb-4 w-full resize-none rounded-xl border border-zinc-700 bg-zinc-950 px-4 py-3 text-sm text-zinc-100 placeholder:text-zinc-600 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 disabled:opacity-50"
          placeholder="Describe the asset to generate…"
        />
        {error && <p className="mb-3 text-sm text-red-400">{error}</p>}
        <button
          onClick={handleGenerate}
          disabled={generating || brief.length < 10}
          className="rounded-xl bg-indigo-600 px-6 py-2.5 text-sm font-medium text-white transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-40"
        >
          {generating ? "Generating…" : "Generate"}
        </button>
      </div>

      {showPipeline && (
        <div className="mb-10 rounded-2xl border border-zinc-800 bg-zinc-900/40 p-6">
          <PipelineVisualizer
            steps={steps}
            activeIndex={activeIndex >= 0 ? activeIndex : steps.length - 1}
            elapsed={elapsed}
          />
        </div>
      )}

      <div>
        <h2 className="mb-4 text-lg font-medium">Assets</h2>
        {assets.length === 0 ? (
          <p className="rounded-xl border border-dashed border-zinc-800 py-12 text-center text-sm text-zinc-500">
            No assets yet. Start the backend and click Generate.
          </p>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2">
            {assets.map((a) => (
              <AssetCard key={a.id} asset={a} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
