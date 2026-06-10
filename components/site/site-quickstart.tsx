import { SectionHeading } from "./site-why"

const steps = [
  {
    title: "Install the package",
    desc: "Clone today; PyPI packaging is the next release milestone.",
    code: `git clone https://github.com/Leon-Drq/openfinagent.git
cd openfinagent
pip install -e .`,
  },
  {
    title: "Run offline first",
    desc: "No network, no data key, no LLM key. Verify the runtime locally.",
    code: `finagent demo NVDA
# writes reports/NVDA-<date>-demo.md
# writes audit.jsonl`,
  },
  {
    title: "Create a workspace",
    desc: "Scaffold config, env template, and live/offline workflows.",
    code: `finagent init my-research-workspace
cd my-research-workspace
finagent demo NVDA`,
  },
  {
    title: "Run live research",
    desc: "Add an OpenAI-compatible key, then fetch public data and draft a memo.",
    code: `cp .env.example .env
# set OPENAI_API_KEY
finagent run earnings-deep-dive \\
  --input ticker=NVDA`,
  },
]

export function SiteQuickstart() {
  return (
    <section id="quickstart" className="border-b border-border bg-secondary/40">
      <div className="mx-auto w-full max-w-6xl px-6 py-20 md:py-28">
        <SectionHeading
          eyebrow="Quickstart"
          title="From zero to a traced report in four steps."
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
            finagent mcp serve
          </code>
        </div>
      </div>
    </section>
  )
}
