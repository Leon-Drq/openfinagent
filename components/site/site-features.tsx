import {
  Bot,
  FileCode2,
  GitBranch,
  Plug,
  ScrollText,
  ShieldCheck,
} from "lucide-react"
import { SectionHeading } from "./site-why"

const features = [
  {
    icon: Bot,
    title: "Multi-agent teams",
    body: "Pre-built Analyst, Quant, Risk Officer, and Macro Strategist roles with role-specific prompts and tool scopes.",
  },
  {
    icon: FileCode2,
    title: "Skill packages",
    body: "Drop-in pip-installable analysis modules: factor models, filings parsers, ETF screeners, credit-spread monitors.",
  },
  {
    icon: GitBranch,
    title: "Workflow DSL",
    body: "Describe a research pipeline in plain YAML. Version it, share it, replay it deterministically.",
  },
  {
    icon: Plug,
    title: "MCP-first integration",
    body: "Works as an MCP server for Claude Code, Cursor, Codex, and any compatible client. No vendor lock-in.",
  },
  {
    icon: ShieldCheck,
    title: "Cost & audit guard",
    body: "Every Discover → Inspect → Call cycle is traced, cached, and budget-capped. No surprise invoices.",
  },
  {
    icon: ScrollText,
    title: "Notebook-first output",
    body: "Reports render as Markdown, Jupyter, or live dashboards. Meet analysts where they already work.",
  },
]

export function SiteFeatures() {
  return (
    <section id="features" className="border-b border-border">
      <div className="mx-auto w-full max-w-6xl px-6 py-20 md:py-28">
        <SectionHeading
          eyebrow="Highlights"
          title="Everything you need to ship a research workflow."
        />

        <div className="mt-14 grid gap-px overflow-hidden rounded-xl border border-border bg-border md:grid-cols-3">
          {features.map((f) => (
            <div
              key={f.title}
              className="flex flex-col gap-4 bg-card p-7 transition-colors hover:bg-secondary/40"
            >
              <f.icon className="h-5 w-5 text-primary" aria-hidden />
              <h3 className="font-serif text-xl tracking-tight">{f.title}</h3>
              <p className="text-sm leading-relaxed text-muted-foreground">
                {f.body}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
