export type LineageNode = {
  run_id: string;
  parent_run_id: string | null;
  status: string;
  created_at: string;
  depth?: number;
};

function statusStyles(status: string) {
  if (status === "approved") {
    return "border-success/35 bg-success/8 text-success";
  }
  if (status === "rejected") {
    return "border-border bg-surface text-muted";
  }
  return "border-warning/35 bg-warning/8 text-warning";
}

function formatTime(iso: string) {
  if (!iso) return "";
  try {
    return new Date(iso).toLocaleString(undefined, {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return "";
  }
}

export function LineageTree({ nodes }: { nodes: LineageNode[] }) {
  if (nodes.length === 0) return null;

  return (
    <div className="mt-8">
      <h3 className="label-caps mb-4 text-muted">Revision lineage</h3>
      <div className="relative space-y-0">
        {nodes.map((node, i) => {
          const isLast = i === nodes.length - 1;
          const depth = node.depth ?? i;
          return (
            <div key={`${node.run_id}-${i}`} className="relative flex gap-4 pb-4">
              <div className="flex w-6 shrink-0 flex-col items-center">
                <div
                  className={`z-10 flex h-6 w-6 items-center justify-center rounded-full border-2 text-[10px] font-bold ${
                    node.status === "approved"
                      ? "border-success bg-success/15 text-success"
                      : "border-border bg-surface-raised text-muted"
                  }`}
                >
                  {depth + 1}
                </div>
                {!isLast && (
                  <div className="mt-1 w-px flex-1 bg-gradient-to-b from-accent/30 to-transparent" />
                )}
              </div>
              <div
                className={`min-w-0 flex-1 rounded-[var(--radius-md)] border px-4 py-3 ${statusStyles(node.status)}`}
              >
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-mono text-sm">{node.run_id.slice(0, 12)}…</span>
                  <span className="label-caps rounded-[var(--radius-sm)] border border-current/20 px-2 py-0.5">
                    {node.status}
                  </span>
                </div>
                {node.parent_run_id && (
                  <p className="mt-1 font-mono text-[11px] opacity-70">
                    parent: {node.parent_run_id.slice(0, 12)}…
                  </p>
                )}
                {node.created_at && (
                  <p className="mt-1 text-[11px] opacity-60">{formatTime(node.created_at)}</p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
