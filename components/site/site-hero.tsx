import Link from "next/link"
import { ArrowUpRight, Github, Terminal } from "lucide-react"
import { Button } from "@/components/ui/button"

export function SiteHero() {
  return (
    <section className="relative overflow-hidden border-b border-border">
      <div className="bg-grain absolute inset-0 opacity-60" aria-hidden />

      <div className="relative mx-auto w-full max-w-6xl px-6 pt-20 pb-24 md:pt-32 md:pb-32">
        {/* eyebrow */}
        <div className="mb-8 flex items-center gap-3">
          <span className="flex h-1.5 w-1.5 rounded-full bg-accent" aria-hidden />
          <span className="font-mono text-xs uppercase tracking-[0.18em] text-muted-foreground">
            Open-source · Apache 2.0 · Pluggable data
          </span>
        </div>

        {/* headline */}
        <h1 className="max-w-5xl font-serif text-5xl leading-[1.02] tracking-tight text-balance md:text-7xl lg:text-[5.5rem]">
          The open-source workspace
          <br className="hidden md:block" />
          {" "}for{" "}
          <span className="italic text-primary">financial agents</span>.
        </h1>

        <p className="mt-8 max-w-3xl text-lg leading-relaxed text-muted-foreground text-pretty md:text-xl">
          Multi-agent teams for research, due diligence, and quant workflows.
          Route across free public data, your private feeds, or{" "}
          <Link
            href="https://qveris.ai"
            target="_blank"
            rel="noreferrer"
            className="border-b border-accent/50 text-foreground hover:border-accent"
          >
            QVeris
          </Link>
          &apos;s{" "}
          <span className="font-mono text-foreground">10,000+</span> verified
          capabilities — behind one SDK, CLI, MCP surface, and upcoming Web UI.
        </p>

        <div className="mt-12 flex flex-wrap items-center gap-3">
          <Button asChild size="lg" className="h-11 gap-2 px-5">
            <Link href="#quickstart">
              <Terminal className="h-4 w-4" aria-hidden />
              Get started
            </Link>
          </Button>
          <Button
            asChild
            size="lg"
            variant="outline"
            className="h-11 gap-2 px-5"
          >
            <Link href="https://github.com/Leon-Drq/openfinagent" target="_blank" rel="noreferrer">
              <Github className="h-4 w-4" aria-hidden />
              View on GitHub
              <ArrowUpRight className="h-3.5 w-3.5" aria-hidden />
            </Link>
          </Button>
          <Link
            href="https://qveris.ai"
            target="_blank"
            rel="noreferrer"
            className="ml-1 inline-flex items-center gap-1 font-mono text-xs text-muted-foreground hover:text-foreground"
          >
            Powered by qveris.ai
            <ArrowUpRight className="h-3 w-3" aria-hidden />
          </Link>
        </div>

        {/* stat strip */}
        <div className="mt-20 grid grid-cols-2 gap-y-6 border-t border-border pt-8 md:grid-cols-4">
          <Stat label="Verified capabilities" value="10,000+" />
          <Stat label="Offline demo" value="0 keys" />
          <Stat label="Built-in providers" value="5" />
          <Stat label="License" value="Apache 2.0" mono={false} />
        </div>
      </div>
    </section>
  )
}

function Stat({
  label,
  value,
  mono = true,
}: {
  label: string
  value: string
  mono?: boolean
}) {
  return (
    <div className="flex flex-col gap-1">
      <span className="font-mono text-[11px] uppercase tracking-wider text-muted-foreground">
        {label}
      </span>
      <span
        className={`text-2xl tracking-tight ${mono ? "font-mono" : "font-serif"}`}
      >
        {value}
      </span>
    </div>
  )
}
