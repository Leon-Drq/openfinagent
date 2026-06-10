import { SectionHeading } from "./site-why"

const steps = [
  {
    title: "Install the package",
    desc: "One pip command. UI extras are optional.",
    code: `pip install openfinagent
# with the Web UI:
pipx install "openfinagent[ui]"`,
  },
  {
    title: "Connect QVeris",
    desc: "OAuth into your QVeris account; verify MCP and budget settings.",
    code: `finagent auth login
finagent doctor`,
  },
  {
    title: "Run a workflow",
    desc: "Stream the agent team as they reason through the task.",
    code: `finagent run examples/earnings-deep-dive.yaml \\
  --ticker NVDA --budget-usd 2.00`,
  },
  {
    title: "Or call from Python",
    desc: "Same engine, embedded in your notebook or service.",
    code: `from finagent import Studio

studio = Studio.from_env()
report = studio.run(
    workflow="earnings-deep-dive",
    inputs={"ticker": "NVDA"},
    budget_usd=2.00,
)
report.to_notebook("nvda.ipynb")`,
  },
]

export function SiteQuickstart() {
  return (
    <section id="quickstart" className="border-b border-border bg-secondary/40">
      <div className="mx-auto w-full max-w-6xl px-6 py-20 md:py-28">
        <SectionHeading
          eyebrow="Quickstart"
          title="From zero to your first report in four steps."
        />

        <ol className="mt-12 grid gap-6 md:grid-cols-2">
          {steps.map((step, i) => (
            <li
              key={step.title}
              className="overflow-hidden rounded-lg border border-border bg-card"
            >
              <div className="flex items-start gap-4 px-6 pt-6">
                <span className="font-mono text-xs text-muted-foreground tabular-nums">
                  {String(i + 1).padStart(2, "0")}
                </span>
                <div>
                  <h3 className="font-serif text-xl tracking-tight">
                    {step.title}
                  </h3>
                  <p className="mt-1 text-sm leading-relaxed text-muted-foreground">
                    {step.desc}
                  </p>
                </div>
              </div>
              <pre className="mt-5 overflow-x-auto border-t border-border bg-secondary/60 p-5 font-mono text-[12.5px] leading-relaxed">
                <code>{step.code}</code>
              </pre>
            </li>
          ))}
        </ol>

        <div className="mt-10 flex flex-wrap items-center gap-3 rounded-lg border border-dashed border-border bg-card p-5 text-sm text-muted-foreground">
          <span className="font-mono text-[11px] uppercase tracking-wider text-foreground">
            MCP server
          </span>
          <span>Run as a server for Claude Code, Cursor, Codex:</span>
          <code className="rounded bg-secondary px-2 py-1 font-mono text-xs">
            finagent mcp serve --port 8765
          </code>
        </div>
      </div>
    </section>
  )
}
