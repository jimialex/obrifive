---
name: Obrifive
description: Multi-tenant SaaS starter with a restrained, trustworthy product UI.
colors:
  terracotta-primary: "#A64B32"
  terracotta-deep: "#7a3220"
  terracotta-accent: "#D97745"
  terracotta-tint: "#FAF6F1"
  ink: "#44403C"
  shell-background: "#F5EFE8"
  surface: "#FAF6F1"
  header-surface: "#FAF6F1"
  muted: "#F0EAE3"
  card: "#FFFCFA"
  muted-foreground: "#8C7B6E"
  border: "#D9CEC2"
  border-soft: "#E8DDD4"
  on-primary: "oklch(1 0 0)"
  success: "oklch(0.626 0.139 155.038)"
  warning: "oklch(0.77 0.18 75.998)"
  destructive: "oklch(0.579 0.214 27.166)"
typography:
  display:
    fontFamily: "Geist, Inter, ui-sans-serif, system-ui, sans-serif"
    fontSize: "1.875rem"
    fontWeight: 600
    lineHeight: 1.15
    letterSpacing: "normal"
  body:
    fontFamily: "Geist, Inter, ui-sans-serif, system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "normal"
---

# Design System: Obrifive

## Direction

The UI is a compact product workbench for authenticated SaaS operations. It
should feel calm, precise and utilitarian: enough density for repeated admin
work, enough polish to feel trustworthy, and no marketing composition inside the
app shell.

## Visual Rules

- The palette is "Terracota & Cemento": terracotta for brand and action over
  warm cement neutrals (cream surfaces, stone ink, sand borders).
- Use terracotta sparingly for active state, focus and primary action. The
  lighter accent (`#D97745`) is the primary in dark mode; in light mode it is a
  brand alias only, not a second action color.
- Prefer warm neutral surfaces, hairline borders and near-flat elevation.
- Keep cards for repeated items, dialogs and genuinely framed tools.
- Do not use decorative gradient blobs, glassmorphism, oversized heroes or generic SaaS illustration.
- Keep text sizes proportional to the container; dashboards and settings screens need compact headings.

## Tokens and themes

- Live tokens are in `frontend/src/app/globals.css`: raw palette variables
  (`--md3-*`) in `:root`, redefined under `.dark`, mapped to semantic Tailwind
  tokens in `@theme inline`. Values in the front matter are the light theme.
- `--obrifive-*` variables (and their `obrifive-*` Tailwind colors) are brand
  aliases of the same palette. Components do not consume them; use the
  semantic tokens below.
- Dark mode is class-based (`next-themes`, `attribute="class"`,
  `defaultTheme="system"`). Every new surface must read correctly in both themes;
  never hardcode a light-only color.
- Components consume semantic tokens (`bg-background`, `bg-primary`,
  `text-foreground`, `text-muted-foreground`, `border-border`,
  `text-destructive`), not `--md3-*` variables. Direct `--md3-*` use is limited
  to a few `shared/ui` primitives that have no semantic token yet (info, field
  indicator, shell background); do not extend it to feature code.

## Typography

Geist is the intended face, but no font file is loaded yet (no `next/font`, no
`@font-face`). The rendered stack is `--font-sans`: Geist or Inter only when
installed locally, otherwise `ui-sans-serif`/`system-ui`. Loading Geist is
pending; until then, do not tune layouts to Geist-specific metrics. Material
Symbols Rounded is loaded from Google Fonts for icons.

## Components

- Navigation: icon + label rows, clear active state, tenant context visible.
- Forms: labelled fields, inline validation, destructive actions separated from primary flows.
- Tables/lists: optimized for scanning, with stable row height and explicit empty states.
- Settings: segmented layout where each panel has one job.
- Internal admin controls should use the same compact component language as the authenticated app.

## Accessibility

Target WCAG 2.1 AA. Preserve keyboard access, visible focus rings, semantic labels,
touch targets, reduced-motion alternatives and readable contrast.

Known debt: in dark mode the primary is `#D97745` with white foreground
(about 3.1:1). That passes for large text and UI components but fails AA for
small text on primary buttons and badges; fixing it needs a darker dark-mode
primary or a dark foreground, checked in both themes.

Known debt: the root `viewport` in `frontend/src/app/layout.tsx` sets
`maximumScale: 1`, which blocks pinch zoom on some mobile browsers and conflicts
with WCAG 1.4.4 (Resize Text). Removing it needs its own change with a mobile
check.
