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
    <div className="grid gap-6 lg:grid-cols-[1fr_260px]">
      <div className="space-y-2">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="label-caps text-muted">Pipeline</h3>
          <span className="font-mono text-sm text-accent">{elapsed.toFixed(1)}s</span>
        </div>
        {steps.map((step, i) => {
          const isActive = i === activeIndex && step.status === "running";
          const isDone = step.status === "complete";
          return (
            <div
              key={`${step.id}-${i}`}
              className={`animate-slide-in flex items-center gap-4 rounded-[var(--radius-md)] border px-4 py-3 ${
                isActive
                  ? "border-accent/40 bg-accent/[0.04] animate-pulse-accent"
                  : isDone
                    ? "border-border bg-surface"
                    : "border-border-subtle bg-transparent opacity-35"
              }`}
              style={{ animationDelay: `${i * 40}ms` }}
            >
              <div
                className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-bold ${
                  isDone
                    ? "bg-success/10 text-success"
                    : isActive
                      ? "bg-ink text-on-accent"
                      : "bg-surface-raised text-muted"
                }`}
              >
                {isDone ? "✓" : i + 1}
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium text-ink">{step.label}</p>
                <p className="text-xs text-muted">{step.provider}</p>
              </div>
            </div>
          );
        })}
      </div>

      <div className="card-raised p-4">
        <h3 className="label-caps mb-3 text-muted">B2 Operations</h3>
        <div className="space-y-2">
          {steps
            .filter((s) => s.b2_op)
            .map((s, i) => (
              <div key={i} className="flex items-start gap-2 text-xs">
                <span
                  className={`mt-0.5 ${s.status === "complete" ? "text-success" : "text-accent"}`}
                >
                  ●
                </span>
                <span className="text-muted">{s.b2_op}</span>
              </div>
            ))}
          {steps.filter((s) => s.b2_op).length === 0 && (
            <p className="text-xs text-muted/60">Waiting for compliance steps…</p>
          )}
        </div>
      </div>
    </div>
  );
}
