# OpenFinAgent Homepage Patterns

Use these patterns as recipes. Translate class names to the target framework when not using Tailwind.

## Tokens

```css
:root {
  --background: oklch(0.985 0.006 85);
  --foreground: oklch(0.18 0.012 60);
  --card: oklch(1 0 0);
  --primary: oklch(0.42 0.11 165);
  --primary-foreground: oklch(0.985 0.006 85);
  --secondary: oklch(0.95 0.008 85);
  --muted-foreground: oklch(0.46 0.012 60);
  --accent: oklch(0.78 0.13 75);
  --border: oklch(0.9 0.008 85);
  --radius: 0.5rem;
}
```

Use:

- `font-serif`: display headlines and important card titles.
- `font-sans`: body and navigation.
- `font-mono`: metrics, tags, labels, code, row numbers.
- `bg-grain`: subtle paper grid/dot texture only; no decorative blobs.

## Hero

Purpose: establish product category and seriousness in the first viewport.

Structure:

- Sticky nav above, compact height around 56px.
- Eyebrow: monospace uppercase metadata, with one tiny accent dot if needed.
- H1: serif, very large, direct product/category statement.
- Body: 2-3 lines, specific nouns, one credible capability number.
- CTAs: primary action and GitHub/source action. Icons allowed only because they clarify button action or brand.
- Stats strip: border top, 2-4 stats, monospace labels.

Avoid:

- Split hero cards.
- Abstract illustration as the main point.
- Generic "AI-powered" headline.
- Gradient background.

## Data Sources / Provider Tiers

Purpose: show coverage model and trust without decorative iconography.

Structure:

- Three cards: free/public, managed capability layer, bring-your-own.
- Top line rule per card; amber for recommended, emerald for private/enterprise path.
- Header row: `Tier 01` and source count.
- Bullet list as numbered rows: `01`, `02`, `03`.
- Examples as small bordered tags.
- Recommended marker as monospace outlined pill, not sparkle icon.

Do not use checkmarks, sparkles, database icons, building icons, or emoji.

## Architecture

Purpose: make the system feel real and replaceable.

Structure:

- Intro plus compact metric strip.
- Left stack: five rows with numeric blocks, title, description, integration tags, and contract tag.
- Highlight the adapter/bridge layer with light emerald tint and border.
- Right panel: execution loop with `Discover -> Inspect -> Call`.
- Use a rail line and numbered nodes, not decorative icons.

Good layer names:

- Interface
- Orchestrator
- Core Runtime
- QVeris Adapter
- Infrastructure

Good contract tags:

- Intent
- Plan
- Trace
- Capability
- Evidence

## Highlights

Purpose: dense feature proof.

Structure:

- Grid separated by `gap-px` on a `bg-border` wrapper.
- Each cell has a `01` style monospace number, serif title, body copy.
- No icons. No hover spectacle. Optional subtle `hover:bg-secondary/40`.

## Quickstart

Purpose: prove the product is usable.

Structure:

- 2-column grid of steps.
- Each step has a number, title, short description, and a code block.
- Code block uses `font-mono`, small type, top border, and muted secondary background.
- Include realistic commands and API calls.

## Comparison

Purpose: clarify positioning.

Structure:

- Use a table, not marketing cards.
- Highlight the product column with a subtle primary tint.
- Prefer text labels (`Yes`, `No`, `Partial`) over icons if the surrounding page has a no-decorative-icons direction.
- Include a short methodology note below.

## CTA

Purpose: close with open-source momentum without hype.

Structure:

- Large serif statement.
- Short body copy.
- One primary action and one secondary action.
- GitHub icon is acceptable in GitHub-specific buttons; avoid decorative social icons elsewhere.

## Copy Voice

Write like a serious builder of financial infrastructure.

Use:

- "workflow", "runtime", "audit", "capability", "provider", "cost guard", "schema", "MCP", "cache".
- Concrete numbers: "10,000+ verified capabilities", "$0.04-$0.31", "Python 3.10+".
- Direct claims that can be tested.

Avoid:

- "revolutionary", "magical", "supercharge", "game-changing".
- Emoji, hype punctuation, and vague AI promises.
- Long explanatory UI text that tells users how the design works.

## Verification Checklist

- Build passes.
- Desktop and mobile screenshots are reviewed.
- No horizontal overflow at 390px width.
- No text overlaps buttons, tags, cards, or adjacent sections.
- Primary content sections have no decorative SVG/icon components.
- Buttons retain icons only when the icon clarifies a command or brand target.
- Section headings and card headings use appropriate scale.
