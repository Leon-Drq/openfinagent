import Link from "next/link"

const cols = [
  {
    title: "Project",
    links: [
      { label: "Documentation", href: "#" },
      { label: "Roadmap", href: "#roadmap" },
      { label: "Changelog", href: "#" },
      { label: "Releases", href: "#" },
    ],
  },
  {
    title: "Community",
    links: [
      { label: "GitHub", href: "https://github.com/Leon-Drq/openfinagent" },
      { label: "Discord", href: "https://discord.gg" },
      { label: "Discussions", href: "#" },
      { label: "Contributing", href: "#" },
    ],
  },
  {
    title: "Resources",
    links: [
      { label: "Skill Hub", href: "#" },
      { label: "Examples", href: "#" },
      { label: "QVeris docs", href: "https://qveris.ai" },
      { label: "MCP spec", href: "https://modelcontextprotocol.io" },
    ],
  },
]

export function SiteFooter() {
  return (
    <footer className="bg-background">
      <div className="mx-auto w-full max-w-6xl px-6 py-16">
        <div className="grid gap-12 md:grid-cols-12">
          <div className="md:col-span-5">
            <div className="flex items-center gap-2">
              <span
                aria-hidden
                className="inline-block h-2.5 w-2.5 rounded-full bg-primary"
              />
              <span className="font-mono text-sm font-medium tracking-tight">
                OpenFinAgent
              </span>
            </div>
            <p className="mt-4 max-w-sm text-sm leading-relaxed text-muted-foreground">
              The open-source financial agent workspace, built on top of QVeris.
              Apache 2.0. Research-only — not investment advice.
            </p>
          </div>

          {cols.map((col) => (
            <div key={col.title} className="md:col-span-2">
              <p className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">
                {col.title}
              </p>
              <ul className="mt-4 space-y-2.5">
                {col.links.map((l) => (
                  <li key={l.label}>
                    <Link
                      href={l.href}
                      className="text-sm text-foreground/80 hover:text-foreground"
                    >
                      {l.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-14 flex flex-col items-start justify-between gap-3 border-t border-border pt-6 font-mono text-[11px] text-muted-foreground md:flex-row md:items-center">
          <span>© {new Date().getFullYear()} OpenFinAgent contributors.</span>
          <span>
            Built with care · Powered by{" "}
            <Link
              href="https://qveris.ai"
              target="_blank"
              rel="noreferrer"
              className="text-foreground hover:underline"
            >
              QVeris
            </Link>
          </span>
        </div>
      </div>
    </footer>
  )
}
