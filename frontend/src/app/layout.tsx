import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import { AppShell } from "@/components/AppShell";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600"],
});

const jetbrains = JetBrains_Mono({
  variable: "--font-jetbrains",
  subsets: ["latin"],
  weight: ["400", "500"],
});

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? "https://attest-black-two.vercel.app";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: "ATTEST — Provenance for the AI-media era",
    template: "%s — ATTEST",
  },
  description:
    "Compliance-grade AI media gateway. Every asset ships with an Ed25519 signature, C2PA-candidate manifest, invisible watermark, and tamper-evident audit trail in Backblaze B2. EU AI Act Article 50 in one pipeline step.",
  applicationName: "ATTEST",
  keywords: [
    "EU AI Act",
    "Article 50",
    "AI provenance",
    "C2PA",
    "Ed25519",
    "content authenticity",
    "Backblaze B2",
    "Genblaze",
  ],
  openGraph: {
    type: "website",
    siteName: "ATTEST",
    title: "ATTEST — Provenance for the AI-media era",
    description:
      "Cryptographic signature, tamper-evident storage, and a public verifier for every AI-generated asset.",
    url: SITE_URL,
  },
  twitter: {
    card: "summary_large_image",
    title: "ATTEST — Provenance for the AI-media era",
    description:
      "Cryptographic signature, tamper-evident storage, and a public verifier for every AI-generated asset.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${jetbrains.variable} h-full`}
    >
      <body className="min-h-full bg-void text-ink antialiased">
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
