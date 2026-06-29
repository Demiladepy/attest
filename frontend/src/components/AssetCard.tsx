import type { Asset } from "@/lib/api";

const STATUS_STYLES: Record<string, { bg: string; text: string; label: string }> = {
  compliant: { bg: "bg-emerald-500/10", text: "text-emerald-400", label: "Compliant" },
  signed: { bg: "bg-indigo-500/10", text: "text-indigo-400", label: "Signed" },
  generating: { bg: "bg-blue-500/10", text: "text-blue-400", label: "Generating" },
  pending: { bg: "bg-zinc-500/10", text: "text-zinc-400", label: "Pending" },
  rejected: { bg: "bg-amber-500/10", text: "text-amber-400", label: "Rejected" },
  tampered: { bg: "bg-red-500/10", text: "text-red-400", label: "Tampered" },
};

export function StatusBadge({ status }: { status: string }) {
  const style = STATUS_STYLES[status] ?? STATUS_STYLES.pending;
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${style.bg} ${style.text}`}>
      {style.label}
    </span>
  );
}

export function AssetCard({ asset }: { asset: Asset }) {
  return (
    <div className="group rounded-xl border border-zinc-800 bg-zinc-900/50 p-5 transition hover:border-zinc-700 hover:bg-zinc-900">
      <div className="mb-3 flex items-start justify-between gap-3">
        <h3 className="font-medium text-zinc-100">{asset.title}</h3>
        <StatusBadge status={asset.status} />
      </div>
      <p className="mb-4 line-clamp-2 text-sm text-zinc-400">{asset.brief}</p>
      <div className="flex flex-wrap gap-2 text-xs text-zinc-500">
        {asset.run_id && <span className="font-mono">run:{asset.run_id.slice(0, 8)}…</span>}
        {asset.sha256 && <span className="font-mono">sha:{asset.sha256.slice(0, 8)}…</span>}
      </div>
    </div>
  );
}
