import type { Metric, OriginalityReport } from "@/lib/types";
import { Badge, Button, Card, Spinner, bandTone } from "./ui";

function scoreColor(score: number) {
  if (score >= 70) return "var(--success)";
  if (score >= 45) return "var(--warning)";
  return "var(--danger)";
}

function ScoreRing({ score }: { score: number }) {
  const r = 46;
  const c = 2 * Math.PI * r;
  const offset = c * (1 - score / 100);
  return (
    <div className="relative h-32 w-32">
      <svg viewBox="0 0 110 110" className="h-full w-full -rotate-90">
        <circle cx="55" cy="55" r={r} fill="none" stroke="var(--line)" strokeWidth="8" />
        <circle
          cx="55"
          cy="55"
          r={r}
          fill="none"
          stroke={scoreColor(score)}
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={c}
          strokeDashoffset={offset}
        />
      </svg>
      <div className="absolute inset-0 grid place-items-center">
        <div className="text-center">
          <div className="text-3xl font-bold" style={{ color: scoreColor(score) }}>{score}</div>
          <div className="text-[10px] uppercase tracking-wide text-muted-2">of 100</div>
        </div>
      </div>
    </div>
  );
}

function MetricRow({ label, m }: { label: string; m: Metric }) {
  return (
    <div>
      <div className="mb-1 flex items-center justify-between text-sm">
        <span className="text-muted">{label}</span>
        <Badge tone={bandTone(m.band)}>{m.band}</Badge>
      </div>
      <div className="h-1.5 w-full overflow-hidden rounded-full bg-surface-solid">
        <div
          className="h-full rounded-full"
          style={{ width: `${Math.round(m.value * 100)}%`, background: "var(--line-strong)" }}
        />
      </div>
    </div>
  );
}

export function OriginalityPanel({
  report,
  onRewrite,
  rewriting,
}: {
  report: OriginalityReport;
  onRewrite: () => void;
  rewriting: boolean;
}) {
  return (
    <Card className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold">Originality Guard</h3>
          <p className="text-xs text-muted-2">Source vs. generated similarity</p>
        </div>
        <Badge tone="accent">ViralReverse exclusive</Badge>
      </div>

      <div className="flex flex-col items-center gap-4 sm:flex-row sm:items-center">
        <ScoreRing score={report.originality_score} />
        <div className="flex-1 space-y-3 self-stretch">
          <MetricRow label="Phrase overlap" m={report.phrase_overlap} />
          <MetricRow label="Distinctive phrase overlap" m={report.distinctive_phrase_overlap} />
          <MetricRow label="Semantic similarity" m={report.semantic_similarity} />
          <MetricRow label="Structural similarity" m={report.structural_similarity} />
        </div>
      </div>

      <p className="rounded-lg border border-line bg-surface-solid p-2.5 text-xs text-muted">
        A higher score means your script is more original — which helps you stay clear of YouTube&apos;s
        reused / inauthentic-content flags. Aim for 70+.
      </p>

      {report.flagged_sections.length > 0 ? (
        <div className="space-y-2">
          <div className="text-sm font-medium">Potentially derivative passages</div>
          {report.flagged_sections.map((f, i) => (
            <div key={i} className="rounded-lg border border-warning/25 bg-warning/5 p-3 text-sm">
              <div className="mb-1 flex items-center gap-2">
                <Badge tone={f.severity === "high" ? "danger" : f.severity === "medium" ? "warning" : "neutral"}>
                  {f.severity}
                </Badge>
                <span className="text-xs text-muted-2">{f.reason}</span>
              </div>
              <span className="text-foreground/90">“{f.script_excerpt}”</span>
            </div>
          ))}
          <Button variant="outline" size="sm" onClick={onRewrite} disabled={rewriting}>
            {rewriting ? <><Spinner /> Rewriting…</> : "Rewrite flagged passages →"}
          </Button>
        </div>
      ) : (
        <div className="rounded-lg border border-success/25 bg-success/5 p-3 text-sm text-emerald-200">
          No derivative passages detected against the source transcript.
        </div>
      )}

      <p className="border-t border-line pt-3 text-xs text-muted-2">{report.disclaimer}</p>
    </Card>
  );
}
