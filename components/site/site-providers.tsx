import { Check, Database, Sparkles, Building2, ArrowRight } from "lucide-react"
import { SectionHeading } from "./site-why"

type Tier = {
  badge: string
  title: string
  tagline: string
  bullets: string[]
  examples: { name: string; note?: string }[]
  accent: "neutral" | "primary" | "accent"
  recommended?: boolean
}

const tiers: Tier[] = [
  {
    badge: "Tier 1",
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
    badge: "Tier 2",
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
    badge: "Tier 3",
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

const tierStyles: Record<Tier["accent"], { ring: string; chip: string; icon: string; iconBg: string }> = {
  neutral: {
    ring: "border-border",
    chip: "bg-secondary text-secondary-foreground",
    icon: "text-muted-foreground",
    iconBg: "bg-secondary",
  },
  accent: {
    ring: "border-accent/40",
    chip: "bg-accent/15 text-accent-foreground border border-accent/30",
    icon: "text-accent",
    iconBg: "bg-accent/15",
  },
  primary: {
    ring: "border-primary/30",
    chip: "bg-primary/10 text-primary border border-primary/20",
    icon: "text-primary",
    iconBg: "bg-primary/10",
  },
}

const tierIcons = {
  "Free & Public": Database,
  QVeris: Sparkles,
  "Bring Your Own": Building2,
} as const

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
            const Icon = tierIcons[tier.title as keyof typeof tierIcons]
            return (
              <div
                key={tier.title}
                className={`relative flex flex-col rounded-xl border bg-card p-7 ${styles.ring} ${
                  tier.recommended ? "shadow-sm" : ""
                }`}
              >
                {tier.recommended && (
                  <span className="absolute -top-3 left-7 inline-flex items-center gap-1.5 rounded-full bg-accent px-3 py-1 text-xs font-medium text-accent-foreground">
                    <Sparkles className="h-3 w-3" aria-hidden />
                    Recommended
                  </span>
                )}

                <div className="flex items-center gap-3">
                  <div className={`flex h-9 w-9 items-center justify-center rounded-lg ${styles.iconBg}`}>
                    <Icon className={`h-4.5 w-4.5 ${styles.icon}`} aria-hidden />
                  </div>
                  <span className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
                    {tier.badge}
                  </span>
                </div>

                <h3 className="mt-5 font-serif text-2xl tracking-tight">{tier.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{tier.tagline}</p>

                <ul className="mt-6 flex flex-col gap-3">
                  {tier.bullets.map((b) => (
                    <li key={b} className="flex items-start gap-2.5 text-sm leading-relaxed">
                      <Check className={`mt-0.5 h-4 w-4 flex-shrink-0 ${styles.icon}`} aria-hidden />
                      <span>{b}</span>
                    </li>
                  ))}
                </ul>

                <div className="mt-7 border-t border-border pt-5">
                  <p className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
                    Examples
                  </p>
                  <div className="mt-3 flex flex-wrap gap-1.5">
                    {tier.examples.map((ex) => (
                      <span
                        key={ex.name}
                        className={`inline-flex items-center gap-1.5 rounded-md px-2 py-1 text-xs ${styles.chip}`}
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

        <div className="mt-10 flex flex-col items-start gap-4 rounded-xl border border-border bg-card p-6 md:flex-row md:items-center md:justify-between">
          <div className="flex items-start gap-4">
            <div className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-lg bg-primary/10">
              <ArrowRight className="h-4.5 w-4.5 text-primary" aria-hidden />
            </div>
            <div>
              <p className="font-serif text-lg tracking-tight">One protocol. Any combination.</p>
              <p className="mt-1 text-sm leading-relaxed text-muted-foreground">
                Declare providers in <span className="font-mono text-xs">config.yaml</span>, set priorities and budget caps,
                and the runtime routes each capability to the cheapest source that can serve it.
              </p>
            </div>
          </div>
          <a
            href="#quickstart"
            className="inline-flex items-center gap-1.5 rounded-md border border-border px-4 py-2 font-mono text-xs uppercase tracking-wider transition-colors hover:bg-secondary"
          >
            See config example
            <ArrowRight className="h-3.5 w-3.5" aria-hidden />
          </a>
        </div>
      </div>
    </section>
  )
}
