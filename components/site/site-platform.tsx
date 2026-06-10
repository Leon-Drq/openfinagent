import { PlatformDiagram } from "./platform-diagram"

export function SitePlatform() {
  return (
    <section id="platform" className="border-t border-border bg-secondary/30">
      <div className="mx-auto max-w-6xl px-6 py-24 md:py-32">
        <header className="mx-auto max-w-3xl text-center">
          <p className="font-mono text-xs uppercase tracking-[0.2em] text-muted-foreground">The Platform</p>
          <h2 className="mt-3 font-serif text-4xl leading-[1.1] tracking-tight text-balance md:text-5xl">
            One workbench,
            <br />
            every financial capability.
          </h2>
          <p className="mt-5 text-pretty text-base leading-relaxed text-muted-foreground md:text-lg">
            QVeris supplies the capability universe up top. The orchestration core in the middle turns it into
            multi-agent workflows. Any front end at the bottom can plug in. Hover the three stages to see what
            happens inside the engine.
          </p>
        </header>

        <div className="mt-14 overflow-hidden rounded-2xl border border-border bg-card shadow-[0_2px_24px_-8px_rgba(0,0,0,0.06)]">
          <div className="border-b border-border bg-secondary/40 px-5 py-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="flex gap-1.5">
                  <span className="h-2.5 w-2.5 rounded-full bg-muted-foreground/30" aria-hidden />
                  <span className="h-2.5 w-2.5 rounded-full bg-muted-foreground/30" aria-hidden />
                  <span className="h-2.5 w-2.5 rounded-full bg-muted-foreground/30" aria-hidden />
                </div>
                <span className="ml-3 font-mono text-xs text-muted-foreground">platform.svg</span>
              </div>
              <span className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                live . animated
              </span>
            </div>
          </div>
          <div className="bg-card p-4 md:p-8">
            <PlatformDiagram />
          </div>
        </div>

        <p className="mt-6 text-center font-mono text-xs text-muted-foreground">
          Hover any stage in the core for details . embeddable as a single SVG file
        </p>
      </div>
    </section>
  )
}
