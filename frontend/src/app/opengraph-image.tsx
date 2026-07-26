import { ImageResponse } from "next/og";

export const alt = "ATTEST — Provenance for the AI-media era";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function OG() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          backgroundColor: "#fdfcfc",
          backgroundImage:
            "radial-gradient(circle at 50% 0%, rgba(14,122,86,0.10), transparent 55%)",
          fontFamily: "sans-serif",
        }}
      >
        {/* Seal */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            width: 132,
            height: 132,
            borderRadius: 999,
            backgroundColor: "#0a0a0a",
            marginBottom: 40,
          }}
        >
          <svg width="72" height="72" viewBox="0 0 24 24" fill="none">
            <path
              d="M5 12.5 L10 17.5 L19 6.5"
              stroke="#ffffff"
              strokeWidth="2.6"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </div>

        <div
          style={{
            fontSize: 88,
            fontWeight: 700,
            letterSpacing: -3,
            color: "#0a0a0a",
            display: "flex",
          }}
        >
          ATTEST
        </div>

        <div
          style={{
            fontSize: 34,
            color: "#6e6e6e",
            marginTop: 12,
            display: "flex",
          }}
        >
          Provenance for the AI-media era.
        </div>

        <div style={{ display: "flex", gap: 16, marginTop: 44 }}>
          {["EU AI Act / Article 50", "Ed25519 signed", "Backblaze B2"].map((t) => (
            <div
              key={t}
              style={{
                display: "flex",
                border: "1px solid #e5e5e5",
                backgroundColor: "#ffffff",
                borderRadius: 999,
                padding: "10px 22px",
                fontSize: 24,
                color: "#0a0a0a",
              }}
            >
              {t}
            </div>
          ))}
        </div>
      </div>
    ),
    { ...size },
  );
}
