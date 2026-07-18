"use client";

import { useEffect, useState } from "react";

const DEADLINE = new Date("2026-08-03T23:59:59Z");

function daysUntil(target: Date) {
  return Math.max(0, Math.ceil((target.getTime() - Date.now()) / (1000 * 60 * 60 * 24)));
}

export function DemoIntroBanner() {
  const [storage, setStorage] = useState<"local" | "b2" | "unknown">("unknown");
  const [pipeline, setPipeline] = useState<"demo" | "gmi" | "replicate">("demo");
  const [b2WriteOk, setB2WriteOk] = useState<boolean | null>(null);
  const days = daysUntil(DEADLINE);

  useEffect(() => {
    const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
    fetch(`${API}/api/health`)
      .then((r) => r.json())
      .then((d: { storage?: string; pipeline?: string; b2_write_ok?: boolean }) => {
        setStorage(d.storage === "b2" ? "b2" : d.storage === "local" ? "local" : "unknown");
        const p = d.pipeline;
        setPipeline(p === "gmi" ? "gmi" : p === "replicate" ? "replicate" : "demo");
        if (typeof d.b2_write_ok === "boolean") setB2WriteOk(d.b2_write_ok);
      })
      .catch(() => setStorage("unknown"));
  }, []);

  const storageLabel =
    storage === "b2" && b2WriteOk === false
      ? "B2 write failed"
      : storage === "b2"
        ? "B2 connected"
        : storage === "local"
          ? "Local dev"
          : "API offline";

  const pipelineLabel =
    pipeline === "gmi"
      ? "GMI Cloud live"
      : pipeline === "replicate"
        ? "FLUX (Replicate)"
        : "Demo mode";

  return (
    <div className="mb-8 overflow-hidden rounded-[var(--radius-lg)] border border-border bg-surface">
      <div className="flex flex-wrap items-center justify-between gap-4 px-5 py-4">
        <div>
          <p className="label-caps text-muted">Backblaze Genblaze Hackathon</p>
          <p className="mt-1 text-sm text-ink/90">
            Generate → sign → verify → tamper. Pipeline powered by GMI Cloud + FLUX when keys are set.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <span className="rounded-full border border-border bg-void px-3 py-1.5 font-mono text-xs text-ink">
            {days}d <span className="text-muted">to submit</span>
          </span>
          <span
            className={`rounded-full border px-3 py-1.5 text-xs font-medium ${
              storage === "b2" && b2WriteOk === false
                ? "border-danger/30 bg-danger/10 text-danger"
                : storage === "b2"
                  ? "border-success/30 bg-success/[0.06] text-success"
                  : storage === "local"
                    ? "border-ink/20 bg-ink/[0.05] text-ink"
                    : "border-border bg-surface text-muted"
            }`}
          >
            {storageLabel}
          </span>
          <span
            className={`rounded-full border px-3 py-1.5 text-xs font-medium ${
              pipeline === "gmi"
                ? "border-ink/20 bg-ink/[0.05] text-ink"
                : "border-border bg-void text-muted"
            }`}
          >
            {pipelineLabel}
          </span>
          <span className="rounded-full border border-border bg-void px-3 py-1.5 text-xs text-muted">
            GMI credits <span className="font-mono text-ink">$5</span>
          </span>
        </div>
      </div>
    </div>
  );
}
