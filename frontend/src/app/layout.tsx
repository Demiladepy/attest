import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "ATTEST — Compliance Console",
  description: "Article 50 compliance-grade AI media gateway",
};

function Nav() {
  return (
    <header className="border-b border-zinc-800 bg-zinc-950/80 backdrop-blur">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-6">
        <Link href="/" className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600 text-sm font-bold text-white">
            A
          </div>
          <span className="font-semibold tracking-tight">ATTEST</span>
        </Link>
        <nav className="flex items-center gap-6 text-sm text-zinc-400">
          <Link href="/" className="transition hover:text-zinc-100">
            Console
          </Link>
          <Link href="/verify" className="transition hover:text-zinc-100">
            Verifier
          </Link>
          <span className="rounded-full bg-amber-500/10 px-2 py-0.5 text-xs text-amber-400">
            Art. 50 · Aug 2, 2026
          </span>
        </nav>
      </div>
    </header>
  );
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${geistSans.variable} ${geistMono.variable} h-full`}>
      <body className="flex min-h-full flex-col bg-zinc-950 text-zinc-100">
        <Nav />
        <main className="flex-1">{children}</main>
      </body>
    </html>
  );
}
