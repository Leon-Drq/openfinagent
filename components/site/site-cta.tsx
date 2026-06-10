import Link from "next/link"
import { ArrowUpRight, Github, MessageSquare } from "lucide-react"
import { Button } from "@/components/ui/button"

export function SiteCTA() {
  return (
    <section className="border-b border-border">
      <div className="relative mx-auto w-full max-w-6xl px-6 py-24 md:py-32">
        <div className="bg-grain pointer-events-none absolute inset-0 opacity-50" aria-hidden />
        <div className="relative flex flex-col items-start gap-8 md:flex-row md:items-end md:justify-between">
          <div className="max-w-2xl">
            <p className="font-mono text-xs uppercase tracking-[0.18em] text-muted-foreground">
              Join the build
            </p>
            <h2 className="mt-4 font-serif text-4xl leading-tight tracking-tight text-balance md:text-6xl">
              Open finance deserves an{" "}
              <span className="italic text-primary">open</span> agent stack.
            </h2>
            <p className="mt-5 max-w-xl leading-relaxed text-muted-foreground">
              Star the repo, ship a Skill, or join the contributors channel on
              Discord. The first 100 contributors get a permanent shout-out in
              the project credits.
            </p>
          </div>

          <div className="flex flex-wrap gap-3">
            <Button asChild size="lg" className="h-11 gap-2 px-5">
              <Link href="https://github.com/Leon-Drq/openfinagent" target="_blank" rel="noreferrer">
                <Github className="h-4 w-4" aria-hidden />
                Star on GitHub
                <ArrowUpRight className="h-3.5 w-3.5" aria-hidden />
              </Link>
            </Button>
            <Button
              asChild
              size="lg"
              variant="outline"
              className="h-11 gap-2 px-5"
            >
              <Link href="https://discord.gg" target="_blank" rel="noreferrer">
                <MessageSquare className="h-4 w-4" aria-hidden />
                Join Discord
              </Link>
            </Button>
          </div>
        </div>
      </div>
    </section>
  )
}
