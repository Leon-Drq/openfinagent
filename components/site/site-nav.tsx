import Link from "next/link"
import { Github } from "lucide-react"
import { Button } from "@/components/ui/button"

export function SiteNav() {
  return (
    <header className="sticky top-0 z-40 border-b border-border/60 bg-background/80 backdrop-blur-md">
      <div className="mx-auto flex h-14 w-full max-w-6xl items-center justify-between px-6">
        <Link href="/" className="flex items-center gap-2">
          <span
            aria-hidden
            className="inline-block h-2.5 w-2.5 rounded-full bg-primary"
          />
          <span className="font-mono text-sm font-medium tracking-tight">
            OpenFinAgent
          </span>
          <span className="ml-2 hidden rounded-full border border-border bg-secondary px-2 py-0.5 font-mono text-[10px] uppercase tracking-wider text-muted-foreground sm:inline-block">
            v0.1 · preview
          </span>
        </Link>

        <nav className="hidden items-center gap-7 text-sm text-muted-foreground md:flex">
          <Link href="#why" className="hover:text-foreground">
            Why
          </Link>
          <Link href="#architecture" className="hover:text-foreground">
            Architecture
          </Link>
          <Link href="#quickstart" className="hover:text-foreground">
            Quickstart
          </Link>
          <Link href="#compare" className="hover:text-foreground">
            Compare
          </Link>
          <Link href="#roadmap" className="hover:text-foreground">
            Roadmap
          </Link>
        </nav>

        <div className="flex items-center gap-2">
          <Button
            asChild
            variant="ghost"
            size="sm"
            className="hidden sm:inline-flex"
          >
            <Link href="#docs">Docs</Link>
          </Button>
          <Button asChild size="sm" className="gap-1.5">
            <Link href="https://github.com/Leon-Drq/openfinagent" target="_blank" rel="noreferrer">
              <Github className="h-3.5 w-3.5" aria-hidden />
              <span>Star</span>
              <span className="ml-1 rounded bg-primary-foreground/15 px-1.5 py-0.5 font-mono text-[10px]">
                0
              </span>
            </Link>
          </Button>
        </div>
      </div>
    </header>
  )
}
