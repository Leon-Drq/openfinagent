import { SectionHeading } from "./site-why"

const layers = [
  {
    label: "Interface",
    code: "Web UI · Notebook · CLI",
    desc: "Where humans (or upstream agents) issue intent.",
  },
  {
    label: "Orchestrator",
    code: "Analyst · Quant · Risk · Macro",
    desc: "Multi-agent role assignment, planning, debate.",
  },
  {
    label: "Core Runtime",
    code: "Skill Registry · Workflow DSL · Memory",
    desc: "Skill resolution, workflow execution, shared context.",
  },
  {
    label: "QVeris Adapter",
    code: "MCP · Python SDK · REST",
    desc: "Discover → Inspect → Call any QVeris capability.",
    accent: true,
  },
  {
    label: "Infrastructure",
    code: "DuckDB Cache · Audit Log · Cost Guard",
    desc: "Caching, observability, budget enforcement.",
  },
]

export function SiteArchitecture() {
  return (
    <section id="architecture" className="border-b border-border bg-secondary/40">
      <div className="mx-auto w-full max-w-6xl px-6 py-20 md:py-28">
        <SectionHeading
          eyebrow="Architecture"
          title="Five layers. Each one replaceable."
        />

        <p className="mt-6 max-w-2xl leading-relaxed text-muted-foreground">
          The runtime is intentionally boring. Every layer talks to the next
          through a stable contract, so you can swap the LLM, the orchestrator,
          or the adapter without rewriting your workflows.
        </p>

        <div className="mt-12 grid gap-10 md:grid-cols-12">
          {/* Layer stack */}
          <ol className="md:col-span-7 space-y-3">
            {layers.map((layer, i) => (
              <li
                key={layer.label}
                className={`group relative flex items-start gap-4 rounded-lg border bg-card p-5 transition-colors ${
                  layer.accent
                    ? "border-accent/60 bg-accent/10"
                    : "border-border"
                }`}
              >
                <span className="font-mono text-[11px] text-muted-foreground tabular-nums">
                  {String(i + 1).padStart(2, "0")}
                </span>
                <div className="flex-1">
                  <div className="flex flex-wrap items-baseline justify-between gap-2">
                    <h3 className="font-serif text-xl tracking-tight">
                      {layer.label}
                    </h3>
                    <code className="font-mono text-xs text-muted-foreground">
                      {layer.code}
                    </code>
                  </div>
                  <p className="mt-1.5 text-sm leading-relaxed text-muted-foreground">
                    {layer.desc}
                  </p>
                </div>
              </li>
            ))}

            {/* QVeris terminus */}
            <li className="ml-6 mt-1 flex items-center gap-3 font-mono text-xs text-muted-foreground">
              <span className="h-px w-8 bg-border" aria-hidden />
              <span className="rounded-full border border-border bg-background px-3 py-1">
                QVeris · 10,000+ capabilities
              </span>
            </li>
          </ol>

          {/* Cycle card */}
          <aside className="md:col-span-5">
            <div className="sticky top-24 rounded-xl border border-border bg-card p-6 shadow-sm">
              <p className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">
                The Discover → Inspect → Call cycle
              </p>

              <ol className="mt-6 space-y-5">
                <CycleStep
                  step="discover"
                  title="Find capabilities"
                  body="Semantic search across the QVeris registry. Returns a shortlist with signatures, costs, and provenance."
                />
                <CycleStep
                  step="inspect"
                  title="Read the contract"
                  body="Fetch the full schema, sample input/output, and rate limits before committing to a call."
                />
                <CycleStep
                  step="call"
                  title="Execute & cache"
                  body="Invoke through MCP. Outputs are tee'd to DuckDB and the audit log. Re-runs hit cache for free."
                />
              </ol>

              <div className="mt-6 flex items-center justify-between border-t border-border pt-4 font-mono text-[11px] text-muted-foreground">
                <span>Average cost / cycle</span>
                <span className="text-foreground">$0.04 – $0.31</span>
              </div>
            </div>
          </aside>
        </div>
      </div>
    </section>
  )
}

function CycleStep({
  step,
  title,
  body,
}: {
  step: string
  title: string
  body: string
}) {
  return (
    <li className="grid grid-cols-[auto_1fr] gap-4">
      <span className="mt-1 inline-flex h-6 items-center rounded-full border border-border bg-background px-2 font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
        {step}
      </span>
      <div>
        <h4 className="font-medium">{title}</h4>
        <p className="mt-1 text-sm leading-relaxed text-muted-foreground">
          {body}
        </p>
      </div>
    </li>
  )
}
