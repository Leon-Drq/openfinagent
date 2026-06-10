import { Check, Minus, X } from "lucide-react"
import { SectionHeading } from "./site-why"

type Cell = "yes" | "partial" | "no" | string

const rows: { feature: string; values: [Cell, Cell, Cell, Cell] }[] = [
  {
    feature: "Open-source license",
    values: ["Apache 2.0", "AGPL / commercial", "MIT", "Apache 2.0"],
  },
  {
    feature: "Multi-agent runtime",
    values: ["yes", "partial", "no", "yes"],
  },
  {
    feature: "Tool / capability breadth",
    values: ["10,000+ via QVeris", "100+ vendors", "no", "few APIs"],
  },
  {
    feature: "Workflow DSL",
    values: ["yes", "no", "no", "no"],
  },
  {
    feature: "Cost & audit guard",
    values: ["yes", "partial", "no", "no"],
  },
  {
    feature: "MCP server",
    values: ["yes", "no", "no", "no"],
  },
  {
    feature: "Production-ready",
    values: ["partial", "yes", "no", "no"],
  },
]

const products = ["OpenFinAgent", "OpenBB", "FinGPT", "TradingAgents"]

export function SiteCompare() {
  return (
    <section id="compare" className="border-b border-border">
      <div className="mx-auto w-full max-w-6xl px-6 py-20 md:py-28">
        <SectionHeading
          eyebrow="Compare"
          title="How we differ from other open finance projects."
        />

        <div className="mt-12 overflow-x-auto rounded-xl border border-border bg-card">
          <table className="w-full border-collapse text-left">
            <thead>
              <tr className="border-b border-border bg-secondary/60">
                <th className="px-5 py-4 font-mono text-[11px] uppercase tracking-wider text-muted-foreground">
                  Feature
                </th>
                {products.map((p, i) => (
                  <th
                    key={p}
                    className={`px-5 py-4 font-mono text-[11px] uppercase tracking-wider ${
                      i === 0
                        ? "bg-primary/10 text-foreground"
                        : "text-muted-foreground"
                    }`}
                  >
                    {p}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.feature} className="border-b border-border last:border-0">
                  <td className="px-5 py-4 text-sm">{row.feature}</td>
                  {row.values.map((v, i) => (
                    <td
                      key={i}
                      className={`px-5 py-4 text-sm ${
                        i === 0 ? "bg-primary/5" : ""
                      }`}
                    >
                      <CellMark value={v} />
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <p className="mt-5 max-w-2xl text-sm leading-relaxed text-muted-foreground">
          Comparison reflects publicly stated capabilities at the time of
          publication. We respect every project on this list — much of our
          design borrows from their lessons.
        </p>
      </div>
    </section>
  )
}

function CellMark({ value }: { value: Cell }) {
  if (value === "yes") {
    return (
      <span className="inline-flex items-center gap-1.5 text-foreground">
        <Check className="h-4 w-4 text-primary" aria-hidden />
        <span className="text-xs font-medium">Yes</span>
      </span>
    )
  }
  if (value === "no") {
    return (
      <span className="inline-flex items-center gap-1.5 text-muted-foreground">
        <X className="h-4 w-4" aria-hidden />
        <span className="text-xs">No</span>
      </span>
    )
  }
  if (value === "partial") {
    return (
      <span className="inline-flex items-center gap-1.5 text-muted-foreground">
        <Minus className="h-4 w-4" aria-hidden />
        <span className="text-xs">Partial</span>
      </span>
    )
  }
  return <span className="font-mono text-xs">{value}</span>
}
