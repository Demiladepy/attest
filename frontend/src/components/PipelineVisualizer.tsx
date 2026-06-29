"use client";

type Step = {
  id: string;
  label: string;
  provider: string;
  status: string;
  b2_op?: string | null;
  detail?: string;
};

export function PipelineVisualizer({
  steps,
  activeIndex,
  elapsed,
}: {
  steps: Step[];
  activeIndex: number;
  elapsed: number;
}) {
  return (
    <div className="grid gap-6 lg:grid-cols-[1fr_280px]">
      <div className="space-y-2">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-sm font-medium text-zinc-300">Pipeline</h3>
          <span className="font-mono text-sm text-indigo-400">{elapsed.toFixed(1)}s</span>
        </div>
        {steps.map((step, i) => {
          const isActive = i === activeIndex && step.status === "running";
          const isDone = step.status === "complete";
          return (
            <div
              key={`${step.id}-${i}`}
              className={`animate-slide-in flex items-center gap-4 rounded-lg border px-4 py-3 ${
                isActive
                  ? "border-indigo-500/50 bg-indigo-500/5 animate-pulse-glow"
                  : isDone
                    ? "border-zinc-800 bg-zinc-900/30"
                    : "border-zinc-800/50 bg-transparent opacity-40"
              }`}
              style={{ animationDelay: `${i * 40}ms` }}
            >
              <div
                className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-bold ${
                  isDone ? "bg-emerald-500/20 text-emerald-400" : isActive ? "bg-indigo-500/20 text-indigo-400" : "bg-zinc-800 text-zinc-500"
                }`}
              >
                {isDone ? "✓" : i + 1}
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium text-zinc-200">{step.label}</p>
                <p className="text-xs text-zinc-500">{step.provider}</p>
              </div>
            </div>
          );
        })}
      </div>

      <div className="rounded-xl border border-zinc-800 bg-zinc-950 p-4">
        <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-zinc-500">B2 Operations</h3>
        <div className="space-y-2">
          {steps
            .filter((s) => s.b2_op)
            .map((s, i) => (
              <div key={i} className="flex items-start gap-2 text-xs">
                <span className={`mt-0.5 ${s.status === "complete" ? "text-emerald-400" : "text-indigo-400"}`}>●</span>
                <span className="text-zinc-400">{s.b2_op}</span>
              </div>
            ))}
          {steps.filter((s) => s.b2_op).length === 0 && (
            <p className="text-xs text-zinc-600">Waiting for compliance steps…</p>
          )}
        </div>
      </div>
    </div>
  );
}
