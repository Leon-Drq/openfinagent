---
name: openfinagent-homepage-design
description: "Apply the OpenFinAgent homepage design system for premium finance and AI product pages. Use when designing, redesigning, or implementing homepage sections, landing pages, README visuals, Next.js/Tailwind components, or UI copy that should match the OpenFinAgent style: restrained editorial finance, warm paper background, serif headlines, monospace metadata, emerald and amber accents, dense proof-oriented sections, no emojis, and no decorative icons."
---

# OpenFinAgent Homepage Design

Use this skill to create or refine product pages in the OpenFinAgent style: premium, restrained, finance-native, and technical without feeling cold. The result should feel like an institutional research tool, not a generic SaaS landing page.

## Design Intent

Optimize for credibility before excitement.

- Lead with the product or category, not marketing abstraction.
- Make the page scannable for technical buyers: capabilities, protocols, architecture, cost, audit, examples.
- Use editorial contrast: large serif statements, compact monospace metadata, quiet body copy.
- Prefer structure over decoration: numbers, rules, tables, rails, code blocks, tags, and data strips.
- Keep interaction affordances familiar and restrained.

## Workflow

1. Audit the current page or requested design.
   - Identify hero, capability proof, data/provider model, architecture, quickstart, comparison, roadmap, and CTA needs.
   - Find anything that feels toy-like: emojis, colorful decorative icons, gradient blobs, oversized rounded cards, stock imagery, vague copy.

2. Establish the visual system.
   - Use warm paper background, deep ink text, emerald primary, amber accent, thin borders, and white cards.
   - Use serif display headlines, sans body copy, and monospace labels.
   - Keep cards at `rounded-lg` or less. Avoid nested cards.

3. Compose sections as product evidence.
   - Hero: clear product/category statement plus proof stats.
   - Platform or architecture: show a system, not feature blurbs.
   - Data sources: show tiers or coverage with numbered lists and tags.
   - Quickstart: show real commands/code.
   - Comparison: use tables and explicit rows.

4. Implement conservatively in the target stack.
   - In Next.js/Tailwind, use existing design tokens and local components first.
   - If a project has shadcn/ui or local `Button`, `Card`, `Table`, use those rather than inventing a parallel system.
   - Use lucide icons only for clear actions or brand targets in buttons. Do not use decorative icons inside content cards.

5. Verify.
   - Run the project build.
   - Check desktop and mobile screenshots.
   - Confirm text does not overflow, overlap, or crowd controls.
   - Confirm content-heavy sections have no horizontal overflow on mobile.
   - For OpenFinAgent-style content sections, decorative SVG/icon counts should usually be zero.

## Non-Negotiables

- Do not use emojis in the UI.
- Do not use decorative icons for tier cards, feature cards, architecture rows, or proof sections.
- Do not add gradient orbs, bokeh blobs, decorative SVG illustrations, or stock-like abstract art.
- Do not make one-note purple, beige, espresso, or dark-slate palettes.
- Do not create a marketing-only landing page when the user asks for a product page or app.
- Do not explain the UI inside the UI. Let the interface communicate through hierarchy and content.
- Do not use hero-scale type inside compact cards or dashboards.

## Core Visual Rules

- Layout: `max-w-6xl`, `px-6`, section padding around `py-20 md:py-28`, and `border-b border-border`.
- Typography: serif for H1/H2 and card titles; sans for body; monospace for labels, stats, tags, code, and section eyebrows.
- Labels: uppercase monospace with `tracking-[0.16em]` to `tracking-[0.18em]`.
- Cards: individual repeated items only; `rounded-lg`, `border`, `bg-card`, subtle or no shadow.
- Proof: use stat strips, tables, code blocks, numbered lists, and source tags.
- Accents: emerald for trust/system state; amber for recommended/highlight; use thin top rules and borders instead of filled badges.

## References

Read `references/patterns.md` when implementing a full page or when recreating a specific section pattern. It contains compact recipes for hero, data tiers, architecture, quickstart, comparison, CTA, color tokens, and copy voice.
