import { SectionHeading } from "./site-why"

type Tier = {
  tier: string
  title: string
  tagline: string
  bullets: string[]
  examples: { name: string; note?: string }[]
  accent: "neutral" | "primary" | "accent"
  recommended?: boolean
}

const tiers: Tier[] = [
  {
    tier: "01",
    title: "Free & Public",
    tagline: "Run the full demo without paying a cent.",
    bullets: [
      "Built-in providers, zero config",
      "API keys are free or not required",
      "Perfect for students & open research",
    ],
    examples: [
      { name: "FRED", note: "macro" },
      { name: "yfinance", note: "equities" },
      { name: "SEC EDGAR", note: "filings" },
      { name: "CoinGecko", note: "crypto" },
      { name: "Alpha Vantage", note: "free tier" },
    ],
    accent: "neutral",
  },
  {
    tier: "02",
    title: "QVeris",
    tagline: "10,000+ verified capabilities, one API key.",
    bullets: [
      "Institutional-grade depth & coverage",
      "Routed via Discover → Inspect → Call",
      "Drop-in upgrade — no workflow rewrite",
    ],
    examples: [
      { name: "Real-time tape" },
      { name: "Deep fundamentals" },
      { name: "Analyst estimates" },
      { name: "Alt-data feeds" },
      { name: "Sell-side research" },
    ],
    accent: "accent",
    recommended: true,
  },
  {
    tier: "03",
    title: "Bring Your Own",
    tagline: "Plug in vendors you already pay for.",
    bullets: [
      "Implement a 30-line Python protocol",
      "Keep proprietary data inside your VPC",
      "Templates for Bloomberg, Refinitiv, internal DBs",
    ],
    examples: [
      { name: "Bloomberg" },
      { name: "Refinitiv" },
      { name: "FactSet" },
      { name: "Internal API" },
      { name: "Custom DB" },
    ],
    accent: "primary",
  },
]

const tierStyles: Record<Tier["accent"], { card: string; rule: string; chip: string; marker: string }> = {
  neutral: {
    card: "border-border",
    rule: "bg-border",
    chip: "border-border bg-background text-muted-foreground",
    marker: "text-muted-foreground",
  },
  accent: {
    card: "border-accent/45 bg-accent/[0.04]",
    rule: "bg-accent",
    chip: "border-accent/25 bg-background text-foreground",
    marker: "text-accent-foreground",
  },
  primary: {
    card: "border-primary/35 bg-primary/[0.04]",
    rule: "bg-primary",
    chip: "border-primary/20 bg-background text-foreground",
    marker: "text-primary",
  },
}

export function SiteProviders() {
  return (
    <section id="data-sources" className="border-b border-border bg-secondary/20">
      <div className="mx-auto w-full max-w-6xl px-6 py-20 md:py-28">
        <SectionHeading
          eyebrow="Data Sources"
          title="Bring your own data — or plug into QVeris for instant coverage."
          description="Three tiers, one unified DataProvider protocol. Mix and match per workflow, route by capability or cost, and never get locked into a single vendor."
        />

        <div className="mt-14 grid gap-6 md:grid-cols-3">
          {tiers.map((tier) => {
            const styles = tierStyles[tier.accent]
            return (
              <div
                key={tier.title}
                className={`relative flex flex-col rounded-lg border bg-card p-7 ${styles.card} ${
                  tier.recommended ? "shadow-sm" : ""
                }`}
              >
                <span
                  aria-hidden
                  className={`absolute inset-x-7 top-0 h-px ${styles.rule}`}
                />

                {tier.recommended && (
                  <span className="absolute -top-3 left-7 rounded-full border border-accent/35 bg-background px-3 py-1 font-mono text-[10px] uppercase tracking-[0.16em] text-accent-foreground">
                    Recommended
                  </span>
                )}

                <div className="flex items-center justify-between gap-4">
                  <span className="font-mono text-xs uppercase tracking-[0.18em] text-muted-foreground">
                    Tier {tier.tier}
                  </span>
                  <span className={`font-mono text-xs ${styles.marker}`}>
                    {tier.examples.length} sources
                  </span>
                </div>

                <h3 className="mt-5 font-serif text-2xl">{tier.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{tier.tagline}</p>

                <ol className="mt-6 flex flex-col gap-3">
                  {tier.bullets.map((b, i) => (
                    <li key={b} className="grid grid-cols-[2rem_1fr] gap-3 text-sm leading-relaxed">
                      <span className="font-mono text-[11px] text-muted-foreground">
                        {String(i + 1).padStart(2, "0")}
                      </span>
                      <span>{b}</span>
                    </li>
                  ))}
                </ol>

                <div className="mt-7 border-t border-border pt-5">
                  <p className="font-mono text-xs uppercase tracking-[0.16em] text-muted-foreground">
                    Examples
                  </p>
                  <div className="mt-3 flex flex-wrap gap-1.5">
                    {tier.examples.map((ex) => (
                      <span
                        key={ex.name}
                        className={`inline-flex items-center gap-1.5 rounded-md border px-2 py-1 text-xs ${styles.chip}`}
                      >
                        {ex.name}
                        {ex.note && (
                          <span className="font-mono text-[10px] opacity-60">{ex.note}</span>
                        )}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            )
          })}
        </div>

        <div className="mt-10 flex flex-col items-start gap-4 rounded-lg border border-border bg-card p-6 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="font-serif text-lg">One protocol. Any combination.</p>
            <p className="mt-1 text-sm leading-relaxed text-muted-foreground">
              Declare providers in <span className="font-mono text-xs">config.yaml</span>, set priorities and budget caps,
              and the runtime routes each capability to the cheapest source that can serve it.
            </p>
          </div>
          <a
            href="#quickstart"
            className="inline-flex items-center gap-1.5 rounded-md border border-border px-4 py-2 font-mono text-xs uppercase tracking-wider transition-colors hover:bg-secondary"
          >
            See config example
          </a>
        </div>
      </div>
    </section>
  )
}
