"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Seal } from "@/components/Seal";

const DEADLINE = new Date("2026-08-03T23:59:59Z");

function daysUntil(target: Date) {
  return Math.max(0, Math.ceil((target.getTime() - Date.now()) / (1000 * 60 * 60 * 24)));
}

const NAV = [
  { href: "/console", label: "Console", desc: "Generate & audit" },
  { href: "/verify", label: "Verifier", desc: "Public verify" },
] as const;

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const days = daysUntil(DEADLINE);

  // Landing page owns its own full-bleed layout (top nav + footer).
  if (pathname === "/") {
    return <>{children}</>;
  }

  return (
    <div className="flex min-h-screen">
      <aside
        className="fixed inset-y-0 left-0 z-40 flex w-[var(--sidebar-w)] flex-col border-r border-border bg-surface print:hidden"
        style={{ width: "var(--sidebar-w)" }}
      >
        <Link href="/" className="flex h-14 items-center gap-2.5 border-b border-border px-5">
          <Seal size={26} className="text-ink" />
          <span className="font-display text-[15px] font-semibold tracking-tight text-ink">ATTEST</span>
        </Link>

        <nav className="flex-1 space-y-0.5 p-3">
          {NAV.map((item) => {
            const active = pathname === item.href || pathname.startsWith(item.href + "/");
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`block rounded-[var(--radius-md)] px-3 py-2.5 transition ${
                  active
                    ? "bg-surface-raised text-ink"
                    : "text-muted hover:bg-surface-raised/60 hover:text-ink"
                }`}
              >
                <span className="block text-sm font-medium">{item.label}</span>
                <span className="block text-[11px] text-muted/80">{item.desc}</span>
              </Link>
            );
          })}
        </nav>

        <div className="space-y-2 border-t border-border p-4">
          <div className="rounded-[var(--radius-md)] border border-border bg-void px-3 py-2">
            <p className="label-caps text-muted">Hackathon</p>
            <p className="mt-1 font-mono text-sm text-ink">
              {days} <span className="text-muted">days left</span>
            </p>
          </div>
          <p className="label-caps text-center text-muted">EU AI Act · Art. 50</p>
        </div>
      </aside>

      <div
        className="print-reset-ml flex min-h-screen flex-1 flex-col bg-ledger"
        style={{ marginLeft: "var(--sidebar-w)" }}
      >
        <main className="flex-1 animate-fade-up">{children}</main>
      </div>
    </div>
  );
}
