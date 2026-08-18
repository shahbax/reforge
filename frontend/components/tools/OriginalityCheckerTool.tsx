"use client";

import { useState } from "react";
import { api, ApiError } from "@/lib/api";
import type { Metric, OriginalityReport } from "@/lib/types";
import { Badge, Button, Card, Spinner, bandTone } from "@/components/ui";

function scoreColor(s: number) {
  return s >= 70 ? "var(--success)" : s >= 45 ? "var(--warning)" : "var(--danger)";
}

function MetricRow({ label, m }: { label: string; m: Metric }) {
  return (
    <div>
      <div className="mb-1 flex items-center justify-between text-sm">
        <span className="text-muted">{label}</span>
        <Badge tone={bandTone(m.band)}>{m.band}</Badge>
      </div>
      <div className="h-1.5 w-full overflow-hidden rounded-full bg-surface-solid">
        <div className="h-full rounded-full" style={{ width: `${Math.round(m.value * 100)}%`, background: "var(--line-strong)" }} />
      </div>
    </div>
  );
}

export function OriginalityCheckerTool() {
  const [source, setSource] = useState("");
  const [generated, setGenerated] = useState("");
  const [report, setReport] = useState<OriginalityReport | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function run() {
    setError(null);
    setBusy(true);
    try {
      setReport(await api.originalityTool(source, generated));
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Something went wrong");
    } finally {
      setBusy(false);
    }
  }

  const ta = "min-h-40 w-full rounded-lg border border-line bg-surface-solid p-3 text-sm text-foreground placeholder:text-muted-2 focus:border-accent/60 focus:outline-none focus:ring-2 focus:ring-accent/20";

  return (
    <div className="space-y-4">
      <div className="grid gap-3 sm:grid-cols-2">
        <div>
          <label className="mb-1.5 block text-sm font-medium">Source text (the original)</label>
          <textarea className={ta} placeholder="Paste the original video's transcript or script…" value={source} onChange={(e) => setSource(e.target.value)} />
        </div>
        <div>
          <label className="mb-1.5 block text-sm font-medium">Your text (the new version)</label>
          <textarea className={ta} placeholder="Paste your script here…" value={generated} onChange={(e) => setGenerated(e.target.value)} />
        </div>
      </div>
      <Button size="lg" onClick={run} disabled={busy || !source.trim() || !generated.trim()}>
        {busy ? <><Spinner /> Checking…</> : "Check originality →"}
      </Button>
      {error && <p className="text-sm text-danger">{error}</p>}

      {report && (
        <Card className="space-y-5">
          <div className="flex items-center gap-4">
            <div className="text-center">
              <div className="text-4xl font-bold" style={{ color: scoreColor(report.originality_score) }}>{report.originality_score}</div>
              <div className="text-xs text-muted-2">of 100</div>
            </div>
            <div className="flex-1 space-y-3">
              <MetricRow label="Phrase overlap" m={report.phrase_overlap} />
              <MetricRow label="Distinctive phrase overlap" m={report.distinctive_phrase_overlap} />
              <MetricRow label="Semantic similarity" m={report.semantic_similarity} />
              <MetricRow label="Structural similarity" m={report.structural_similarity} />
            </div>
          </div>
          {report.flagged_sections.length > 0 ? (
            <div className="space-y-2">
              <div className="text-sm font-medium">Potentially derivative passages</div>
              {report.flagged_sections.map((f, i) => (
                <div key={i} className="rounded-lg border border-warning/25 bg-warning/5 p-3 text-sm">
                  <Badge tone={f.severity === "high" ? "danger" : f.severity === "medium" ? "warning" : "neutral"}>{f.severity}</Badge>
                  <span className="ml-2 text-foreground/90">“{f.script_excerpt}”</span>
                </div>
              ))}
            </div>
          ) : (
            <div className="rounded-lg border border-success/25 bg-success/5 p-3 text-sm text-emerald-200">No derivative passages detected.</div>
          )}
          <p className="border-t border-line pt-3 text-xs text-muted-2">{report.disclaimer}</p>
        </Card>
      )}
    </div>
  );
}
