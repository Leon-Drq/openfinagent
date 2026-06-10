/**
 * PlatformDiagram
 * ---------------
 * Pure-SVG, self-contained, animated platform overview.
 * - viewBox 0 0 1200 820, fully responsive
 * - SMIL + CSS animations: marching-ants flow lines, traveling dots,
 *   rotating-stage highlight in the core, pulsing glow
 * - Hover popovers on the three orchestration stages (Discover / Inspect / Call)
 * - Uses CSS custom properties so it auto-themes with the design tokens
 */
export function PlatformDiagram() {
  // ---------- TOP TIER : capability chips ----------
  const topChips = [
    { label: "Market Data", note: "OHLCV . L1/L2" },
    { label: "Filings", note: "10-K . 10-Q . 8-K" },
    { label: "News", note: "wires . sentiment" },
    { label: "Macro", note: "FRED . BLS . IMF" },
    { label: "Crypto", note: "spot . onchain" },
    { label: "Alt Data", note: "ESG . satellite" },
  ]
  const topY = 56
  const topH = 56
  const topW = 170
  const topGap = 24
  const topStartX = (1200 - (topChips.length * topW + (topChips.length - 1) * topGap)) / 2

  // ---------- LEFT : agents ----------
  const agents = [
    { label: "Analyst", note: "research & narrative" },
    { label: "Quant", note: "factors & backtests" },
    { label: "Risk Officer", note: "limits & compliance" },
    { label: "Macro Strategist", note: "regimes & flows" },
  ]
  const agentX = 40
  const agentW = 240
  const agentH = 56
  const agentStartY = 280
  const agentGap = 18

  // ---------- RIGHT : skills ----------
  const skills = [
    { label: "Factor Library", note: "momentum . value . quality" },
    { label: "Valuation Models", note: "DCF . comps . multiples" },
    { label: "Company Deep-Dive", note: "earnings . 13F . ownership" },
    { label: "Workflow DSL", note: "YAML . replayable" },
  ]
  const skillX = 920
  const skillW = 240

  // ---------- BOTTOM : surfaces ----------
  const surfaces = [
    { label: "Web UI", note: "Next.js" },
    { label: "Notebook", note: "Jupyter . Marimo" },
    { label: "CLI", note: "qfin run" },
    { label: "MCP Server", note: "stdio . http" },
    { label: "REST API", note: "OpenAPI" },
  ]
  const surfY = 728
  const surfH = 54
  const surfW = 200
  const surfGap = 16
  const surfStartX = (1200 - (surfaces.length * surfW + (surfaces.length - 1) * surfGap)) / 2

  // ---------- CORE ----------
  const coreX = 340
  const coreY = 270
  const coreW = 520
  const coreH = 330

  // ---------- STAGES with hover detail ----------
  const stages = [
    {
      name: "DISCOVER",
      note: "find capabilities . semantic match",
      detail: [
        "Semantic search across 10,000+ tools",
        "Auto-rank by recency, coverage, cost",
        "No hard-coded API list to maintain",
      ],
    },
    {
      name: "INSPECT",
      note: "validate cost . permissions . schema",
      detail: [
        "Pre-flight cost & rate-limit check",
        "Type-safe schema for inputs/outputs",
        "Permission scope before any call",
      ],
    },
    {
      name: "CALL",
      note: "execute . cache . trace . audit",
      detail: [
        "Local cache to avoid redundant credits",
        "OpenTelemetry trace for every call",
        "Replayable from the audit log",
      ],
    },
  ]

  return (
    <svg
      viewBox="0 0 1200 820"
      role="img"
      aria-label="Platform diagram: capability universe, orchestration core, agents, skills, and surfaces"
      className="block h-auto w-full"
      xmlns="http://www.w3.org/2000/svg"
    >
      <defs>
        <style>{`
          .label-tier { font: 600 11px ui-monospace, SFMono-Regular, Menlo, monospace; letter-spacing: .12em; text-transform: uppercase; fill: var(--muted-foreground); }
          .label-chip { font: 600 13px Inter, system-ui, sans-serif; fill: var(--foreground); }
          .label-chip-note { font: 500 10px ui-monospace, SFMono-Regular, monospace; fill: var(--muted-foreground); letter-spacing: .04em; }
          .label-core-title { font: 700 14px Inter, system-ui, sans-serif; fill: var(--primary-foreground); letter-spacing: .04em; text-transform: uppercase; }
          .label-stage { font: 600 15px Inter, system-ui, sans-serif; fill: var(--primary-foreground); }
          .label-stage-note { font: 400 11px ui-monospace, SFMono-Regular, monospace; fill: color-mix(in oklch, var(--primary-foreground) 70%, transparent); }
          .label-popover-title { font: 700 11px ui-monospace, SFMono-Regular, monospace; letter-spacing: .14em; text-transform: uppercase; fill: var(--accent); }
          .label-popover-line { font: 500 11px Inter, system-ui, sans-serif; fill: var(--foreground); }

          .chip-bg { fill: var(--card); stroke: var(--border); stroke-width: 1; }
          .chip-bg-amber { fill: color-mix(in oklch, var(--accent) 14%, var(--card)); stroke: color-mix(in oklch, var(--accent) 50%, var(--border)); stroke-width: 1; }
          .chip-bg-emerald { fill: color-mix(in oklch, var(--primary) 8%, var(--card)); stroke: color-mix(in oklch, var(--primary) 35%, var(--border)); stroke-width: 1; }

          .flow-line {
            stroke: color-mix(in oklch, var(--primary) 55%, var(--border));
            stroke-width: 1.25;
            fill: none;
            stroke-dasharray: 4 6;
            animation: dash 1.6s linear infinite;
          }
          @keyframes dash { to { stroke-dashoffset: -20; } }

          .core-rect { fill: var(--primary); }
          .core-glow {
            fill: none;
            stroke: var(--primary);
            stroke-width: 2;
            opacity: 0.35;
            animation: glow 2.6s ease-in-out infinite;
            transform-origin: 600px 435px;
            transform-box: fill-box;
          }
          @keyframes glow {
            0%, 100% { opacity: 0.15; transform: scale(1); }
            50%      { opacity: 0.55; transform: scale(1.02); }
          }

          .stage-row { cursor: pointer; }
          .stage-highlight {
            fill: color-mix(in oklch, var(--accent) 90%, transparent);
            opacity: 0;
            animation: stage-cycle 4.8s ease-in-out infinite;
            transform-box: fill-box;
          }
          .stage-1 { animation-delay: 0s; }
          .stage-2 { animation-delay: 1.6s; }
          .stage-3 { animation-delay: 3.2s; }
          @keyframes stage-cycle {
            0%, 25%   { opacity: 0; transform: translateX(-4px); }
            8%, 17%   { opacity: 1; transform: translateX(0); }
            33%, 100% { opacity: 0; transform: translateX(4px); }
          }

          /* Hover popovers for stages */
          .stage-popover {
            opacity: 0;
            pointer-events: none;
            transition: opacity .2s ease, transform .2s ease;
            transform: translateY(4px);
            transform-box: fill-box;
          }
          .stage-row:hover .stage-popover {
            opacity: 1;
            transform: translateY(0);
          }
          .stage-row:hover .stage-highlight {
            animation: none;
            opacity: 1;
            transform: translateX(0);
          }

          .dot { fill: var(--accent); }
          .dot-emerald { fill: var(--primary); }

          .chip-hover { transition: transform .25s ease; transform-origin: center; transform-box: fill-box; }
          .chip-group:hover .chip-hover { transform: translateY(-2px); }
          .chip-group:hover .chip-bg,
          .chip-group:hover .chip-bg-amber,
          .chip-group:hover .chip-bg-emerald { stroke: var(--primary); }
        `}</style>

        <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="color-mix(in oklch, var(--primary) 55%, var(--border))" />
        </marker>
      </defs>

      {/* ============================================================== */}
      {/*                  TOP TIER : Capability Universe                  */}
      {/* ============================================================== */}
      <text x="600" y="28" textAnchor="middle" className="label-tier">
        Capability Universe — powered by QVeris . 10,000+ verified tools
      </text>

      {topChips.map((chip, i) => {
        const x = topStartX + i * (topW + topGap)
        return (
          <g key={chip.label} className="chip-group">
            <g className="chip-hover">
              <rect x={x} y={topY} width={topW} height={topH} rx={10} className="chip-bg-amber" />
              <text x={x + 16} y={topY + 24} className="label-chip">
                {chip.label}
              </text>
              <text x={x + 16} y={topY + 42} className="label-chip-note">
                {chip.note}
              </text>
              <circle cx={x + topW - 14} cy={topY + 14} r={3} className="dot" />
            </g>
          </g>
        )
      })}

      {topChips.map((_, i) => {
        const cx = topStartX + i * (topW + topGap) + topW / 2
        return <line key={`drop-${i}`} x1={cx} y1={topY + topH} x2={cx} y2={180} className="flow-line" />
      })}
      <line
        x1={topStartX + topW / 2}
        y1={180}
        x2={topStartX + (topChips.length - 1) * (topW + topGap) + topW / 2}
        y2={180}
        className="flow-line"
      />
      <line x1={600} y1={180} x2={600} y2={coreY} className="flow-line" markerEnd="url(#arrow)" />

      <circle r={3.5} className="dot">
        <animateMotion
          dur="3.2s"
          repeatCount="indefinite"
          path={`M ${topStartX + topW / 2} 180 L ${
            topStartX + (topChips.length - 1) * (topW + topGap) + topW / 2
          } 180`}
        />
      </circle>
      <circle r={3.5} className="dot">
        <animateMotion
          dur="3.2s"
          begin="1.6s"
          repeatCount="indefinite"
          path={`M ${
            topStartX + (topChips.length - 1) * (topW + topGap) + topW / 2
          } 180 L ${topStartX + topW / 2} 180`}
        />
      </circle>
      <circle r={3.5} className="dot-emerald">
        <animateMotion dur="1.6s" repeatCount="indefinite" path={`M 600 180 L 600 ${coreY}`} />
      </circle>

      {/* ============================================================== */}
      {/*                      MIDDLE TIER : 3 columns                     */}
      {/* ============================================================== */}

      {/* ---- Left column : Agents ---- */}
      <text x={agentX} y={agentStartY - 22} className="label-tier">
        Agents
      </text>
      {agents.map((a, i) => {
        const y = agentStartY + i * (agentH + agentGap)
        return (
          <g key={a.label} className="chip-group">
            <g className="chip-hover">
              <rect x={agentX} y={y} width={agentW} height={agentH} rx={8} className="chip-bg-emerald" />
              <text x={agentX + 16} y={y + 24} className="label-chip">
                {a.label}
              </text>
              <text x={agentX + 16} y={y + 42} className="label-chip-note">
                {a.note}
              </text>
              <circle cx={agentX + agentW - 14} cy={y + agentH / 2} r={3} className="dot-emerald" />
            </g>
            <line
              x1={agentX + agentW}
              y1={y + agentH / 2}
              x2={coreX}
              y2={y + agentH / 2}
              className="flow-line"
              markerEnd="url(#arrow)"
            />
            <circle r={3} className="dot-emerald">
              <animateMotion
                dur={`${2.2 + i * 0.2}s`}
                begin={`${i * 0.4}s`}
                repeatCount="indefinite"
                path={`M ${agentX + agentW} ${y + agentH / 2} L ${coreX} ${y + agentH / 2}`}
              />
            </circle>
          </g>
        )
      })}

      {/* ---- Right column : Skills ---- */}
      <text x={skillX} y={agentStartY - 22} className="label-tier">
        Skills . Workflows
      </text>
      {skills.map((s, i) => {
        const y = agentStartY + i * (agentH + agentGap)
        return (
          <g key={s.label} className="chip-group">
            <g className="chip-hover">
              <rect x={skillX} y={y} width={skillW} height={agentH} rx={8} className="chip-bg-amber" />
              <text x={skillX + 16} y={y + 24} className="label-chip">
                {s.label}
              </text>
              <text x={skillX + 16} y={y + 42} className="label-chip-note">
                {s.note}
              </text>
              <circle cx={skillX + skillW - 14} cy={y + agentH / 2} r={3} className="dot" />
            </g>
            <line
              x1={coreX + coreW}
              y1={y + agentH / 2}
              x2={skillX}
              y2={y + agentH / 2}
              className="flow-line"
              markerEnd="url(#arrow)"
            />
            <circle r={3} className="dot">
              <animateMotion
                dur={`${2.4 + i * 0.2}s`}
                begin={`${0.2 + i * 0.4}s`}
                repeatCount="indefinite"
                path={`M ${coreX + coreW} ${y + agentH / 2} L ${skillX} ${y + agentH / 2}`}
              />
            </circle>
          </g>
        )
      })}

      {/* ---- Center : Studio Core ---- */}
      <rect
        x={coreX - 6}
        y={coreY - 6}
        width={coreW + 12}
        height={coreH + 12}
        rx={18}
        className="core-glow"
      />
      <rect x={coreX} y={coreY} width={coreW} height={coreH} rx={14} className="core-rect" />

      <text x={coreX + coreW / 2} y={coreY + 30} textAnchor="middle" className="label-core-title">
        Studio Core . Orchestration Engine
      </text>
      <line
        x1={coreX + 24}
        y1={coreY + 46}
        x2={coreX + coreW - 24}
        y2={coreY + 46}
        stroke="color-mix(in oklch, var(--primary-foreground) 25%, transparent)"
        strokeWidth={1}
      />

      {stages.map((stage, i) => {
        const sy = coreY + 80 + i * 78
        const popX = coreX + 286
        const popY = sy - 28
        const popW = 218
        const popH = 88
        return (
          <g key={stage.name} className="stage-row">
            {/* invisible hit-target spanning the row */}
            <rect
              x={coreX + 16}
              y={sy - 22}
              width={coreW - 32}
              height={64}
              fill="transparent"
            />

            {/* highlight bar (animated) */}
            <rect
              x={coreX + 22}
              y={sy - 18}
              width={4}
              height={56}
              rx={2}
              className={`stage-highlight stage-${i + 1}`}
            />
            {/* index badge */}
            <circle
              cx={coreX + 50}
              cy={sy + 8}
              r={14}
              fill="color-mix(in oklch, var(--primary-foreground) 12%, transparent)"
              stroke="color-mix(in oklch, var(--primary-foreground) 35%, transparent)"
              strokeWidth={1}
            />
            <text
              x={coreX + 50}
              y={sy + 12}
              textAnchor="middle"
              fontFamily="ui-monospace, SFMono-Regular, monospace"
              fontWeight={600}
              fontSize={11}
              fill="var(--primary-foreground)"
            >
              {`0${i + 1}`}
            </text>
            <text x={coreX + 78} y={sy + 6} className="label-stage">
              {stage.name}
            </text>
            <text x={coreX + 78} y={sy + 26} className="label-stage-note">
              {stage.note}
            </text>
            {i < 2 && (
              <line
                x1={coreX + 50}
                y1={sy + 24}
                x2={coreX + 50}
                y2={sy + 60}
                stroke="color-mix(in oklch, var(--primary-foreground) 35%, transparent)"
                strokeWidth={1}
                strokeDasharray="2 3"
              />
            )}

            {/* Hover popover (right side of stage row) */}
            <g className="stage-popover">
              {/* connector line */}
              <line
                x1={coreX + 280}
                y1={sy + 8}
                x2={popX}
                y2={sy + 8}
                stroke="var(--accent)"
                strokeWidth={1}
                opacity={0.6}
              />
              <rect
                x={popX}
                y={popY}
                width={popW}
                height={popH}
                rx={8}
                fill="var(--card)"
                stroke="var(--accent)"
                strokeWidth={1.25}
              />
              <text x={popX + 14} y={popY + 18} className="label-popover-title">
                {stage.name} DETAILS
              </text>
              {stage.detail.map((line, j) => (
                <text
                  key={j}
                  x={popX + 14}
                  y={popY + 36 + j * 16}
                  className="label-popover-line"
                >
                  {`. ${line}`}
                </text>
              ))}
            </g>
          </g>
        )
      })}

      <line
        x1={coreX + 24}
        y1={coreY + coreH - 44}
        x2={coreX + coreW - 24}
        y2={coreY + coreH - 44}
        stroke="color-mix(in oklch, var(--primary-foreground) 25%, transparent)"
        strokeWidth={1}
      />
      <text
        x={coreX + coreW / 2}
        y={coreY + coreH - 22}
        textAnchor="middle"
        fontFamily="ui-monospace, SFMono-Regular, monospace"
        fontSize={10}
        fill="color-mix(in oklch, var(--primary-foreground) 75%, transparent)"
        letterSpacing="0.18em"
      >
        CACHE . AUDIT LOG . COST GUARD . OBSERVABILITY
      </text>

      {/* ============================================================== */}
      {/*                    BOTTOM TIER : Surfaces                        */}
      {/* ============================================================== */}

      <line
        x1={600}
        y1={coreY + coreH}
        x2={600}
        y2={698}
        className="flow-line"
        markerEnd="url(#arrow)"
      />
      <line
        x1={surfStartX + surfW / 2}
        y1={698}
        x2={surfStartX + (surfaces.length - 1) * (surfW + surfGap) + surfW / 2}
        y2={698}
        className="flow-line"
      />
      {surfaces.map((_, i) => {
        const cx = surfStartX + i * (surfW + surfGap) + surfW / 2
        return <line key={`down-${i}`} x1={cx} y1={698} x2={cx} y2={surfY} className="flow-line" />
      })}

      <text x={600} y={686} textAnchor="middle" className="label-tier">
        Surfaces — choose any front-end
      </text>
      {surfaces.map((s, i) => {
        const x = surfStartX + i * (surfW + surfGap)
        return (
          <g key={s.label} className="chip-group">
            <g className="chip-hover">
              <rect x={x} y={surfY} width={surfW} height={surfH} rx={10} className="chip-bg" />
              <text x={x + 16} y={surfY + 22} className="label-chip">
                {s.label}
              </text>
              <text x={x + 16} y={surfY + 40} className="label-chip-note">
                {s.note}
              </text>
              <circle cx={x + surfW - 14} cy={surfY + 14} r={3} className="dot-emerald" />
            </g>
          </g>
        )
      })}

      <circle r={3.5} className="dot-emerald">
        <animateMotion
          dur="3.6s"
          repeatCount="indefinite"
          path={`M 600 ${coreY + coreH} L 600 698 L ${surfStartX + surfW / 2} 698`}
        />
      </circle>
      <circle r={3.5} className="dot-emerald">
        <animateMotion
          dur="3.6s"
          begin="1.2s"
          repeatCount="indefinite"
          path={`M 600 ${coreY + coreH} L 600 698 L ${
            surfStartX + (surfaces.length - 1) * (surfW + surfGap) + surfW / 2
          } 698`}
        />
      </circle>
      <circle r={3.5} className="dot-emerald">
        <animateMotion
          dur="3.6s"
          begin="2.4s"
          repeatCount="indefinite"
          path={`M 600 ${coreY + coreH} L 600 698 L ${
            surfStartX + 2 * (surfW + surfGap) + surfW / 2
          } 698`}
        />
      </circle>
    </svg>
  )
}
