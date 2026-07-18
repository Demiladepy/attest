---
version: alpha
name: ATTEST Command
description: Regulatory command center for EU AI Act Article 50 media compliance
colors:
  void: "#0A0A0A"
  surface: "#111111"
  surface-raised: "#1A1A1A"
  border: "#2E2E2E"
  border-subtle: "#222222"
  ink: "#F4F4F5"
  muted: "#8A8A8E"
  accent: "#D4FF33"
  accent-dim: "#A8C428"
  on-accent: "#0A0A0A"
  success: "#4ADE80"
  danger: "#F87171"
  warning: "#FBBF24"
typography:
  display-lg:
    fontFamily: Bricolage Grotesque
    fontSize: 1.75rem
    fontWeight: 600
    letterSpacing: -0.02em
  display-md:
    fontFamily: Bricolage Grotesque
    fontSize: 1.25rem
    fontWeight: 600
    letterSpacing: -0.01em
  body:
    fontFamily: Figtree
    fontSize: 0.9375rem
    fontWeight: 400
    lineHeight: 1.6
  label-caps:
    fontFamily: Figtree
    fontSize: 0.6875rem
    fontWeight: 600
    letterSpacing: 0.12em
  mono:
    fontFamily: JetBrains Mono
    fontSize: 0.8125rem
    fontWeight: 400
rounded:
  sm: 6px
  md: 10px
  lg: 14px
spacing:
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
components:
  button-primary:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.on-accent}"
    rounded: "{rounded.md}"
    padding: 12px
  button-primary-hover:
    backgroundColor: "{colors.accent-dim}"
    textColor: "{colors.on-accent}"
  button-ghost:
    backgroundColor: transparent
    textColor: "{colors.muted}"
    rounded: "{rounded.md}"
  card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.lg}"
  input:
    backgroundColor: "{colors.void}"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
  sidebar-active:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.on-accent}"
    rounded: "{rounded.sm}"
---

## Overview

ATTEST Command is a regulatory operations console — not a generic SaaS dashboard. The UI reads like a **compliance control room**: deep void backgrounds, a single luminous lime accent (aligned with GMI Cloud / hackathon partner aesthetics), and monospace for cryptographic artifacts. Judges should feel they're inside infrastructure that takes Article 50 seriously.

## Colors

- **Void (#0A0A0A):** Page background. Absolute black-green undertone.
- **Surface (#111111):** Cards, panels, inputs at rest.
- **Accent (#D4FF33):** Primary actions, active nav, pipeline pulse. One accent only — never indigo or purple.
- **Ink / Muted:** High-contrast body copy vs metadata, timestamps, hashes.
- **Success / Danger / Warning:** Verification states only — never decorative.

## Typography

- **Bricolage Grotesque** for headings — mechanical warmth, not corporate neutral.
- **Figtree** for UI copy — legible at small sizes in dense panels.
- **JetBrains Mono** for `run_id`, SHA-256, URLs — never for paragraphs.

## Layout

- Fixed **left sidebar** (220px) with Console + Verifier. Main content scrolls independently.
- Subtle **dot-grid** on void background — suggests audit trail / ledger without noise.
- Max content width ~1200px; verifier page narrower (~720px) for focus.

## Elevation & Depth

- Borders over shadows. Depth via `surface` → `surface-raised` and 1px `#2E2E2E` edges.
- Active pipeline step gets accent glow, not drop shadow.

## Shapes

- Rounded corners 10–14px on cards; 6px on chips and nav pills.
- Status badges are pill-shaped; buttons are rounded rectangles.

## Components

- Primary CTA: lime fill, black text, bold weight.
- Ghost buttons: border only, for secondary actions (Revise, Refresh).
- Cards: no gradient fills except the hackathon strip (accent at 8% opacity).

## Do's and Don'ts

- **Do** use accent sparingly — one focal element per viewport region.
- **Do** keep the SSE pipeline visualizer prominent; it's the demo hero.
- **Don't** use indigo, purple, or blue as primary accent.
- **Don't** use Inter, Geist, or system-ui as display fonts.
