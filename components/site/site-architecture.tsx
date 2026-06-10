import {
  Activity,
  ArrowDown,
  CheckCircle2,
  Cpu,
  Database,
  FileSearch,
  GitBranch,
  Layers3,
  MousePointer2,
  Network,
  PlugZap,
  Search,
} from "lucide-react"
import { SectionHeading } from "./site-why"

const layers = [
  {
    label: "Interface",
    code: "Web UI · Notebook · CLI",
    desc: "Where humans or upstream agents issue intent.",
    contract: "Intent",
    icon: MousePointer2,
  },
  {
    label: "Orchestrator",
    code: "Analyst · Quant · Risk · Macro",
    desc: "Multi-agent role assignment, planning, and debate.",
    contract: "Plan",
    icon: Network,
  },
  {
    label: "Core Runtime",
    code: "Skill Registry · Workflow DSL · Memory",
    desc: "Skill resolution, workflow execution, shared context.",
    contract: "Trace",
    icon: Cpu,
  },
  {
    label: "QVeris Adapter",
    code: "MCP · Python SDK · REST",
    desc: "Discover, inspect, then call any QVeris capability.",
    contract: "Capability",
    icon: PlugZap,
    accent: true,
  },
  {
    label: "Infrastructure",
    code: "DuckDB Cache · Audit Log · Cost Guard",
    desc: "Caching, observability, and budget enforcement.",
    contract: "Evidence",
    icon: Database,
  },
]

const cycle = [
  {
    step: "Discover",
    title: "Find the right capability",
    body: "Semantic search ranks tools by coverage, freshness, provenance, and estimated cost.",
    icon: Search,
  },
  {
    step: "Inspect",
    title: "Read the contract",
    body: "Schemas, sample payloads, limits, and permission scope are checked before execution.",
    icon: FileSearch,
  },
  {
    step: "Call",
    title: "Execute, cache, audit",
    body: "Calls run through MCP, write to DuckDB, and leave a replayable audit trail.",
    icon: CheckCircle2,
  },
]

const metrics = [
  { label: "Verified tools", value: "10k+" },
  { label: "Avg cycle", value: "$0.04–$0.31" },
  { label: "Replay trail", value: "JSONL" },
]

export function SiteArchitecture() {
  return (
    <section id="architecture" className="border-b border-border bg-secondary/35">
      <div className="mx-auto w-full max-w-6xl px-6 py-20 md:py-28">
        <div className="grid gap-8 md:grid-cols-12 md:items-end">
          <div className="md:col-span-7">
            <SectionHeading
              eyebrow="Architecture"
              title="Five layers. One stable execution loop."
            />
            <p className="mt-6 max-w-2xl leading-relaxed text-muted-foreground">
              OpenFinAgent keeps the runtime modular without making the system
              feel loose. Each layer owns one contract, and the QVeris adapter
              turns that contract into a Discover, Inspect, Call cycle.
            </p>
          </div>

          <div className="md:col-span-5">
            <div className="grid overflow-hidden rounded-lg border border-border bg-card sm:grid-cols-3">
              {metrics.map((metric) => (
                <div
                  key={metric.label}
                  className="border-b border-border px-4 py-3 last:border-b-0 sm:border-r sm:border-b-0 sm:last:border-r-0"
                >
                  <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-muted-foreground">
                    {metric.label}
                  </p>
                  <p className="mt-1 whitespace-nowrap font-mono text-sm text-foreground">
                    {metric.value}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="mt-12 grid gap-8 lg:grid-cols-12">
          <ol className="relative space-y-3 lg:col-span-7">
            <span
              aria-hidden
              className="absolute left-6 top-8 hidden h-[calc(100%-4rem)] w-px bg-border md:block"
            />
            {layers.map((layer, i) => (
              <LayerRow key={layer.label} layer={layer} index={i} />
            ))}
          </ol>

          <aside className="lg:col-span-5">
            <div className="sticky top-24 overflow-hidden rounded-lg border border-border bg-card shadow-sm">
              <div className="border-b border-border bg-secondary/50 px-5 py-4">
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-muted-foreground">
                      Execution Loop
                    </p>
                    <h3 className="mt-1 font-serif text-2xl leading-none">
                      Discover → Inspect → Call
                    </h3>
                  </div>
                  <Activity className="h-5 w-5 text-primary" aria-hidden />
                </div>
              </div>

              <ol className="relative px-5 py-6">
                <span
                  aria-hidden
                  className="absolute left-[1.9rem] top-10 h-[calc(100%-5rem)] w-px bg-border"
                />
                {cycle.map((item, i) => (
                  <CycleStep key={item.step} item={item} index={i} />
                ))}
              </ol>

              <div className="grid grid-cols-[1fr_auto_1fr] items-center border-t border-border bg-secondary/35 px-5 py-4">
                <div>
                  <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-muted-foreground">
                    Input
                  </p>
                  <p className="mt-1 text-sm">Research intent</p>
                </div>
                <ArrowDown className="h-4 w-4 rotate-[-90deg] text-muted-foreground" />
                <div className="text-right">
                  <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-muted-foreground">
                    Output
                  </p>
                  <p className="mt-1 text-sm">Audited evidence</p>
                </div>
              </div>
            </div>
          </aside>
        </div>
      </div>
    </section>
  )
}

function LayerRow({
  layer,
  index,
}: {
  layer: (typeof layers)[number]
  index: number
}) {
  const Icon = layer.icon

  return (
    <li
      className={`relative grid grid-cols-[3rem_1fr] gap-4 rounded-lg border p-4 md:grid-cols-[3.5rem_1fr_auto] md:items-center md:p-5 ${
        layer.accent
          ? "border-primary/45 bg-primary/[0.06] shadow-[0_0_0_1px_color-mix(in_oklch,var(--primary)_18%,transparent)]"
          : "border-border bg-card"
      }`}
    >
      <div>
        <span
          className={`relative z-10 grid h-12 w-12 place-items-center rounded-lg border ${
            layer.accent
              ? "border-primary/40 bg-primary text-primary-foreground"
              : "border-border bg-secondary text-muted-foreground"
          }`}
        >
          <Icon className="h-5 w-5" aria-hidden />
        </span>
        <span className="font-mono text-[11px] text-muted-foreground md:mt-2 md:block">
          {String(index + 1).padStart(2, "0")}
        </span>
      </div>

      <div>
        <div className="flex flex-wrap items-center gap-3">
          <h3 className="font-serif text-xl leading-tight">{layer.label}</h3>
          {layer.accent && (
            <span className="inline-flex items-center gap-1 rounded-full border border-primary/25 bg-background px-2.5 py-1 font-mono text-[10px] uppercase tracking-[0.14em] text-primary">
              <Layers3 className="h-3 w-3" aria-hidden />
              bridge
            </span>
          )}
        </div>
        <p className="mt-1.5 text-sm leading-relaxed text-muted-foreground">
          {layer.desc}
        </p>
      </div>

      <div className="col-span-2 flex flex-wrap items-center gap-2 md:col-span-1 md:justify-end">
        <span className="rounded-full border border-border bg-background px-3 py-1 font-mono text-[11px] text-muted-foreground">
          {layer.code}
        </span>
        <span className="inline-flex items-center gap-1 rounded-full border border-border bg-secondary px-3 py-1 font-mono text-[11px] text-foreground">
          <GitBranch className="h-3 w-3 text-primary" aria-hidden />
          {layer.contract}
        </span>
      </div>
    </li>
  )
}

function CycleStep({
  item,
  index,
}: {
  item: (typeof cycle)[number]
  index: number
}) {
  const Icon = item.icon

  return (
    <li className="relative grid grid-cols-[2.5rem_1fr] gap-4 pb-6 last:pb-0">
      <span className="relative z-10 grid h-10 w-10 place-items-center rounded-lg border border-border bg-background text-primary">
        <Icon className="h-4 w-4" aria-hidden />
      </span>
      <div>
        <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-muted-foreground">
          0{index + 1} · {item.step}
        </p>
        <h4 className="mt-1 font-medium">{item.title}</h4>
        <p className="mt-1.5 text-sm leading-relaxed text-muted-foreground">
          {item.body}
        </p>
      </div>
    </li>
  )
}
