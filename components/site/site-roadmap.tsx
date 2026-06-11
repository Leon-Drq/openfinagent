import { SectionHeading } from "./site-why"

const milestones = [
  {
    version: "v0.1",
    status: "Shipped",
    state: "done" as const,
    bullets: [
      "CLI · core runtime",
      "init · demo · doctor",
      "5 providers",
      "MCP server",
    ],
  },
  {
    version: "v0.2",
    status: "In progress",
    state: "active" as const,
    bullets: [
      "PyPI release",
      "release workflow",
      "package verification",
    ],
  },
  {
    version: "v0.3",
    status: "Planned",
    state: "todo" as const,
    bullets: [
      "Skill registry",
      "workflow templates",
      "provider catalog",
    ],
  },
  {
    version: "v0.4",
    status: "Planned",
    state: "todo" as const,
    bullets: [
      "Web workbench",
      "audit timeline",
      "report preview",
    ],
  },
  {
    version: "v1.0",
    status: "Vision",
    state: "todo" as const,
    bullets: [
      "team controls",
      "signed skills",
      "on-prem bridge",
    ],
  },
]

export function SiteRoadmap() {
  return (
    <section id="roadmap" className="border-b border-border bg-secondary/40">
      <div className="mx-auto w-full max-w-6xl px-6 py-20 md:py-28">
        <SectionHeading
          eyebrow="Roadmap"
          title="The path from first run to production workflow."
        />

        <ol className="mt-14 grid gap-6 md:grid-cols-5">
          {milestones.map((m) => (
            <li
              key={m.version}
              className={`flex flex-col gap-4 rounded-lg border bg-card p-5 ${
                m.state === "active"
                  ? "border-primary/50 ring-1 ring-primary/20"
                  : "border-border"
              }`}
            >
              <div className="flex items-baseline justify-between">
                <span className="font-mono text-lg tracking-tight">
                  {m.version}
                </span>
                <StatusDot state={m.state} />
              </div>
              <span
                className={`font-mono text-[10px] uppercase tracking-wider ${
                  m.state === "done"
                    ? "text-primary"
                    : m.state === "active"
                      ? "text-accent-foreground"
                      : "text-muted-foreground"
                }`}
              >
                {m.status}
              </span>
              <ul className="space-y-1.5 text-sm text-muted-foreground">
                {m.bullets.map((b) => (
                  <li key={b} className="leading-snug">
                    — {b}
                  </li>
                ))}
              </ul>
            </li>
          ))}
        </ol>

        <p className="mt-10 max-w-2xl text-sm leading-relaxed text-muted-foreground">
          The community votes on priorities every quarter. Open an issue with
          the <code className="rounded bg-card px-1.5 py-0.5 font-mono text-xs">vote</code> label
          to weigh in.
        </p>
      </div>
    </section>
  )
}

function StatusDot({ state }: { state: "done" | "active" | "todo" }) {
  const cls =
    state === "done"
      ? "bg-primary"
      : state === "active"
        ? "bg-accent ring-4 ring-accent/30"
        : "bg-muted-foreground/30"
  return <span className={`h-2 w-2 rounded-full ${cls}`} aria-hidden />
}
