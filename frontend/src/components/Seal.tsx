"use client";

/**
 * ATTEST identity mark — a cryptographic certification seal.
 * Concentric rings + tick guilloché + a signed checkmark. currentColor-based.
 */
export function Seal({
  size = 40,
  animated = false,
  className = "",
}: {
  size?: number;
  animated?: boolean;
  className?: string;
}) {
  const ticks = Array.from({ length: 48 });
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 100 100"
      fill="none"
      className={className}
      aria-hidden="true"
    >
      {/* outer ring */}
      <circle cx="50" cy="50" r="47" stroke="currentColor" strokeOpacity="0.25" strokeWidth="1.5" />
      {/* rotating tick guilloché */}
      <g className={animated ? "animate-seal-ring" : ""}>
        {ticks.map((_, i) => {
          const a = (i / ticks.length) * Math.PI * 2;
          const r1 = 40;
          const r2 = i % 4 === 0 ? 33 : 36.5;
          return (
            <line
              key={i}
              x1={50 + r1 * Math.cos(a)}
              y1={50 + r1 * Math.sin(a)}
              x2={50 + r2 * Math.cos(a)}
              y2={50 + r2 * Math.sin(a)}
              stroke="currentColor"
              strokeOpacity="0.35"
              strokeWidth="1.2"
            />
          );
        })}
      </g>
      {/* inner disc */}
      <circle cx="50" cy="50" r="27" stroke="currentColor" strokeOpacity="0.9" strokeWidth="2" />
      {/* signed checkmark */}
      <path
        d="M38 51 L47 60 L64 40"
        stroke="currentColor"
        strokeWidth="5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

/** Compact square logo lockup for the sidebar/nav. */
export function SealMark({ size = 28 }: { size?: number }) {
  return (
    <span
      className="inline-flex items-center justify-center rounded-lg bg-ink text-on-accent"
      style={{ width: size + 8, height: size + 8 }}
    >
      <Seal size={size} className="text-on-accent" />
    </span>
  );
}
