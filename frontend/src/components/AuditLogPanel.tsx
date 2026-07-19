"use client";

import { useCallback, useEffect, useState } from "react";
import { fetchAuditLog } from "@/lib/api";

type AuditEntry = {
  id: string;
  event_type: string;
  detail: string;
  created_at: string;
  run_id?: string | null;
  b2_object_key?: string | null;
};

const EVENT_LABELS: Record<string, string> = {
  generated: "Generated",
  manifest_written: "Manifest written",
  signed: "Signed",
  watermarked: "Watermarked",
  c2pa_embedded: "C2PA embedded",
  object_lock_applied: "Object Lock",
  verified: "Verified",
  tamper_detected: "Tamper detected",
  rejected: "Rejected",
};

export function AuditLogPanel({ refreshKey }: { refreshKey: number }) {
  const [entries, setEntries] = useState<AuditEntry[]>([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await fetchAuditLog();
      setEntries(data);
    } catch {
      setEntries([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- async fetch-on-mount; state updates occur after await
    load();
  }, [load, refreshKey]);

  return (
    <div className="card p-5">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="font-display text-sm font-semibold text-ink">Audit log</h2>
        <button type="button" onClick={load} className="btn-ghost px-2 py-1 text-xs">
          Refresh
        </button>
      </div>
      {loading ? (
        <p className="text-sm text-muted">Loading…</p>
      ) : entries.length === 0 ? (
        <p className="text-sm text-muted">No events yet. Generate an asset to populate the trail.</p>
      ) : (
        <div className="max-h-96 space-y-2 overflow-y-auto">
          {entries.map((e) => (
            <div
              key={e.id}
              className="rounded-[var(--radius-md)] border border-border-subtle bg-void px-3 py-2 text-xs"
            >
              <div className="mb-1 flex items-center justify-between gap-2">
                <span className="font-semibold text-accent">
                  {EVENT_LABELS[e.event_type] ?? e.event_type}
                </span>
                <span className="shrink-0 font-mono text-[10px] text-muted">
                  {new Date(e.created_at).toLocaleTimeString()}
                </span>
              </div>
              {e.detail && <p className="truncate font-mono text-[11px] text-muted">{e.detail}</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
