import Link from "next/link";
import { Seal } from "@/components/Seal";

function Step({ n, title, body }: { n: string; title: string; body: string }) {
  return (
    <div className="relative">
      <div className="mb-3 flex h-9 w-9 items-center justify-center rounded-full border border-border bg-surface font-mono text-sm text-ink shadow-sm-soft">
        {n}
      </div>
      <h3 className="font-display text-[15px] font-medium text-ink">{title}</h3>
      <p className="mt-1.5 text-sm leading-relaxed text-muted">{body}</p>
    </div>
  );
}

function Feature({ title, body }: { title: string; body: string }) {
  return (
    <div className="card card-hover p-5">
      <h3 className="font-display text-[15px] font-medium text-ink">{title}</h3>
      <p className="mt-2 text-sm leading-relaxed text-muted">{body}</p>
    </div>
  );
}

export default function LandingPage() {
  return (
    <div className="hero-ground min-h-screen">
      {/* Top nav */}
      <header className="mx-auto flex max-w-6xl items-center justify-between px-6 py-5">
        <div className="flex items-center gap-2.5">
          <Seal size={30} className="text-ink" />
          <span className="font-display text-[17px] font-semibold tracking-tight text-ink">ATTEST</span>
        </div>
        <nav className="flex items-center gap-2">
          <Link href="/verify" className="btn-ghost hidden sm:inline-flex">
            Verify an asset
          </Link>
          <Link href="/console" className="btn-primary">
            Open Console
          </Link>
        </nav>
      </header>

      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="grid-fade pointer-events-none absolute inset-0" />
        <div className="relative mx-auto max-w-4xl px-6 pb-16 pt-16 text-center sm:pt-24">
          <div className="mb-8 flex justify-center">
            <Seal size={104} animated className="text-ink" />
          </div>
          <div className="mb-5 flex flex-wrap justify-center gap-2">
            <span className="chip">EU AI Act · Article 50</span>
            <span className="chip">Ed25519 signed</span>
            <span className="chip">Backblaze B2 Object Lock</span>
          </div>
          <h1 className="font-display mx-auto max-w-3xl text-[2.75rem] font-light leading-[1.05] tracking-[-0.03em] text-ink sm:text-[3.5rem]">
            Provenance for the
            <br />
            AI-media era.
          </h1>
          <p className="mx-auto mt-6 max-w-xl text-base leading-relaxed text-muted">
            Every asset your pipeline generates leaves with a cryptographic signature, a C2PA-candidate
            manifest, an invisible watermark, and a tamper-evident audit trail in object storage you
            control. Compliance as a three-second pipeline step — not a legal risk.
          </p>
          <div className="mt-9 flex flex-wrap justify-center gap-3">
            <Link href="/console" className="btn-primary btn-lg">
              Generate &amp; sign an asset
            </Link>
            <Link href="/verify" className="btn-ghost btn-lg">
              Verify one instead →
            </Link>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="mx-auto max-w-6xl px-6 py-16">
        <p className="label-caps mb-2 text-center text-muted">How it works</p>
        <h2 className="font-display mb-12 text-center text-2xl font-light tracking-[-0.02em] text-ink">
          Four steps, one durable record
        </h2>
        <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
          <Step
            n="1"
            title="Generate"
            body="A brief runs through the Genblaze pipeline — classified and generated on GMI Cloud, with fallback chains."
          />
          <Step
            n="2"
            title="Sign"
            body="The ComplianceSink canonicalizes the manifest and signs it with an Ed25519 key only your pipeline holds."
          />
          <Step
            n="3"
            title="Store"
            body="Asset and signed manifest land in Backblaze B2 under Object Lock — durable, retained, tamper-evident."
          />
          <Step
            n="4"
            title="Verify"
            body="Anyone can re-hash the bytes, check the signature, and walk the revision lineage. No account required."
          />
        </div>
      </section>

      {/* Proof / tamper teaser */}
      <section className="mx-auto max-w-6xl px-6 pb-16">
        <div className="card shadow-md-soft overflow-hidden">
          <div className="grid items-center gap-8 p-8 sm:p-12 lg:grid-cols-[1.2fr_1fr]">
            <div>
              <p className="label-caps mb-3 text-attested">The proof</p>
              <h2 className="font-display text-2xl font-light leading-tight tracking-[-0.02em] text-ink sm:text-3xl">
                Change one byte, and the seal breaks.
              </h2>
              <p className="mt-4 max-w-lg text-sm leading-relaxed text-muted">
                The public verifier re-computes the SHA-256 of the asset and checks it against the
                signed manifest. Re-encode, crop, or splice a single pixel and verification flips to a
                red <span className="font-medium text-danger">Tamper detected</span> — while the original
                stays provably intact in B2.
              </p>
              <Link href="/verify" className="btn-primary mt-7 inline-flex">
                Try the verifier
              </Link>
            </div>
            <div className="flex items-center justify-center gap-6">
              <div className="text-center">
                <div className="mb-2 flex h-16 w-16 items-center justify-center rounded-full border-2 border-attested bg-attested-soft text-2xl text-attested">
                  ✓
                </div>
                <p className="font-mono text-[11px] text-muted">VERIFIED</p>
              </div>
              <div className="text-muted">→</div>
              <div className="text-center">
                <div className="mb-2 flex h-16 w-16 items-center justify-center rounded-full border-2 border-danger bg-danger/[0.06] text-2xl text-danger">
                  ✗
                </div>
                <p className="font-mono text-[11px] text-muted">TAMPERED</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="mx-auto max-w-6xl px-6 pb-20">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <Feature
            title="Ed25519 authorship"
            body="Mode 2 signing proves an asset came from your pipeline's key — not just that its bytes are intact."
          />
          <Feature
            title="Tamper-evident storage"
            body="Manifests sit under B2 Object Lock (governance, 365-day retention). The audit trail is append-only."
          />
          <Feature
            title="Revision lineage"
            body="Reject-and-retry links every run to its parent. The verifier renders the full ancestry tree."
          />
          <Feature
            title="C2PA-candidate manifest"
            body="Structured provenance today, aligned to the C2PA claim model for a drop-in Mode 3 tomorrow."
          />
          <Feature
            title="Invisible watermark"
            body="A detectable watermark rides in the pixels, surviving format conversions the hash alone would miss."
          />
          <Feature
            title="Public verifier"
            body="A paste-a-URL page anyone can use — regulators, partners, auditors. No login, no SDK."
          />
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-6 py-8 sm:flex-row">
          <div className="flex items-center gap-2.5">
            <Seal size={22} className="text-ink" />
            <span className="font-display text-sm font-medium text-ink">ATTEST</span>
            <span className="text-sm text-muted">· Compliance-grade AI media gateway</span>
          </div>
          <div className="flex items-center gap-5 text-sm text-muted">
            <Link href="/console" className="hover:text-ink">
              Console
            </Link>
            <Link href="/verify" className="hover:text-ink">
              Verifier
            </Link>
            <a
              href="https://github.com/Demiladepy/attest"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-ink"
            >
              GitHub
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
