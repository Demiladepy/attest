import Link from "next/link";
import type { Asset } from "@/lib/api";

const STATUS_STYLES: Record<string, { bg: string; text: string; label: string }> = {
  compliant: { bg: "bg-success/10", text: "text-success", label: "Compliant" },
  signed: { bg: "bg-accent/10", text: "text-accent", label: "Signed" },
  generating: { bg: "bg-accent/5", text: "text-accent-dim", label: "Generating" },
  pending: { bg: "bg-surface-raised", text: "text-muted", label: "Pending" },
  rejected: { bg: "bg-warning/10", text: "text-warning", label: "Rejected" },
  tampered: { bg: "bg-danger/10", text: "text-danger", label: "Tampered" },
};

export function StatusBadge({ status }: { status: string }) {
  const style = STATUS_STYLES[status] ?? STATUS_STYLES.pending;
  return (
    <span
      className={`inline-flex items-center rounded-full border border-border px-2.5 py-0.5 text-[11px] font-semibold uppercase tracking-wide ${style.bg} ${style.text}`}
    >
      {style.label}
    </span>
  );
}

export function AssetCard({
  asset,
  onRevise,
}: {
  asset: Asset;
  onRevise?: (asset: Asset) => void;
}) {
  const verifyHref = asset.asset_url
    ? `/verify?asset=${encodeURIComponent(asset.asset_url)}&manifest=${encodeURIComponent(asset.manifest_url ?? "")}`
    : null;

  return (
    <div className="card group overflow-hidden p-0 transition hover:border-muted/40 hover:bg-surface-raised">
      {asset.asset_url && (
        <div className="relative aspect-video w-full overflow-hidden border-b border-border bg-void">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={asset.asset_url}
            alt={asset.title}
            className="h-full w-full object-cover"
            loading="lazy"
          />
        </div>
      )}
      <div className="p-5">
      <div className="mb-3 flex items-start justify-between gap-3">
        <h3 className="font-display text-sm font-semibold text-ink">{asset.title}</h3>
        <StatusBadge status={asset.status} />
      </div>
      <p className="mb-4 line-clamp-2 text-sm leading-relaxed text-muted">{asset.brief}</p>
      <div className="mb-4 flex flex-wrap gap-2 font-mono text-[11px] text-muted">
        {asset.run_id && <span>run:{asset.run_id.slice(0, 8)}…</span>}
        {asset.sha256 && <span>sha:{asset.sha256.slice(0, 8)}…</span>}
        {asset.parent_run_id && (
          <span className="text-warning/80">parent:{asset.parent_run_id.slice(0, 8)}…</span>
        )}
      </div>
      <div className="flex flex-wrap gap-4">
        {verifyHref && (
          <Link
            href={verifyHref}
            className="text-xs font-semibold text-accent transition hover:text-accent-dim"
          >
            Verify →
          </Link>
        )}
        {onRevise && asset.run_id && asset.status === "compliant" && (
          <button
            type="button"
            onClick={() => onRevise(asset)}
            className="text-xs font-semibold text-warning transition hover:text-warning/80"
          >
            Revise (reject &amp; retry)
          </button>
        )}
      </div>
      </div>
    </div>
  );
}
