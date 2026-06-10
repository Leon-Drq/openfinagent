import { SectionHeading } from "./site-why"

const features = [
  {
    title: "Offline first run",
    body: "Run a deterministic demo report without network access, data credentials, or an LLM key.",
  },
  {
    title: "Provider protocol",
    body: "Route one workflow across sample data, free public providers, QVeris, or private feeds through the same interface.",
  },
  {
    title: "Workflow DSL",
    body: "Describe a research pipeline in plain YAML. Version it, share it, replay it deterministically.",
  },
  {
    title: "MCP-first integration",
    body: "Works as an MCP server for Claude Code, Cursor, Codex, and any compatible client. No vendor lock-in.",
  },
  {
    title: "Cost & audit guard",
    body: "Every Discover → Inspect → Call cycle is traced, cached, and budget-capped. No surprise invoices.",
  },
  {
    title: "Report artifacts",
    body: "Every run can produce Markdown reports and JSONL audit logs that are easy to inspect, diff, and archive.",
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
          {features.map((f, i) => (
            <div
              key={f.title}
              className="flex flex-col gap-4 bg-card p-7 transition-colors hover:bg-secondary/40"
            >
              <span className="font-mono text-[11px] uppercase tracking-[0.16em] text-muted-foreground">
                {String(i + 1).padStart(2, "0")}
              </span>
              <h3 className="font-serif text-xl">{f.title}</h3>
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
