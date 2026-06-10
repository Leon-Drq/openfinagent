export function SiteWhy() {
  return (
    <section id="why" className="border-b border-border">
      <div className="mx-auto w-full max-w-6xl px-6 py-20 md:py-28">
        <SectionHeading
          eyebrow="Why OpenFinAgent"
          title="Stop gluing data vendors together. Start shipping research."
        />

        <div className="mt-12 grid gap-10 md:grid-cols-12">
          <div className="md:col-span-7">
            <p className="text-lg leading-relaxed text-muted-foreground md:text-xl text-pretty">
              Building a useful financial AI agent today means stitching
              together broken pieces — vendor SDKs, brittle scrapers, hand-rolled
              tool definitions, no audit trail, no cost ceiling, no way to share
              workflows with a teammate. OpenFinAgent fixes that by standing
              on two shoulders.
            </p>

            <ul className="mt-8 space-y-5">
              <Pillar
                tag="01"
                title="QVeris as the capability layer"
                body="10,000+ pre-verified tools across market data, fundamentals, filings, alternative data, and execution venues — accessible through a single MCP / SDK call."
              />
              <Pillar
                tag="02"
                title="A purpose-built agent runtime"
                body="YAML workflows, role-specific LLM steps, audit logs, cost guards, and a planned Skill registry / Web workbench for analysts and quants."
              />
              <Pillar
                tag="03"
                title="Production-grade by default"
                body="Every Discover → Inspect → Call cycle is traced, cached, and budget-capped. Bring your own LLM, your own data, your own infra."
              />
            </ul>
          </div>

          <div className="md:col-span-5">
            <div className="sticky top-24 rounded-xl border border-border bg-card p-6 shadow-sm">
              <p className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">
                Before / After
              </p>

              <div className="mt-5 space-y-5">
                <div>
                  <p className="text-sm text-muted-foreground line-through">
                    500 lines of glue code, three SDKs, a Pandas script, a
                    Slack message to ops asking for a CSV.
                  </p>
                </div>

                <div className="border-t border-border pt-5">
                  <p className="font-mono text-[11px] uppercase tracking-wider text-primary">
                    With OpenFinAgent
                  </p>
                  <pre className="mt-3 overflow-x-auto rounded-md bg-secondary p-4 font-mono text-[12px] leading-relaxed">
                    <code>
                      <span className="text-muted-foreground"># first run, no external services</span>{"\n"}
                      finagent demo <span className="text-primary">NVDA</span>{"\n\n"}
                      <span className="text-muted-foreground"># live workflow after setting OPENAI_API_KEY</span>{"\n"}
                      finagent run earnings-deep-dive \\{"\n"}
                      {"  "}--input ticker=<span className="text-primary">NVDA</span>
                    </code>
                  </pre>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

function Pillar({
  tag,
  title,
  body,
}: {
  tag: string
  title: string
  body: string
}) {
  return (
    <li className="grid grid-cols-[auto_1fr] gap-5 border-t border-border pt-5">
      <span className="font-mono text-xs text-muted-foreground">{tag}</span>
      <div>
        <h3 className="font-serif text-xl tracking-tight">{title}</h3>
        <p className="mt-2 leading-relaxed text-muted-foreground">{body}</p>
      </div>
    </li>
  )
}

export function SectionHeading({
  eyebrow,
  title,
  description,
}: {
  eyebrow: string
  title: string
  description?: string
}) {
  return (
    <div className="max-w-3xl">
      <p className="font-mono text-xs uppercase tracking-[0.18em] text-muted-foreground">
        {eyebrow}
      </p>
      <h2 className="mt-4 font-serif text-3xl leading-tight tracking-tight text-balance md:text-5xl">
        {title}
      </h2>
      {description && (
        <p className="mt-5 max-w-2xl leading-relaxed text-muted-foreground">
          {description}
        </p>
      )}
    </div>
  )
}
