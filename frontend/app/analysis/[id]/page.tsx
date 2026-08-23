"use client";

import { use, useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { api, ApiError, startCheckout } from "@/lib/api";
import type { AnalysisView, ScriptControls, ScriptView } from "@/lib/types";
import { TopNav } from "@/components/TopNav";
import { useRequireAuth } from "@/components/AuthProvider";
import { supabaseEnabled } from "@/lib/supabase";
import { Badge, Button, Card, Spinner, StatusBadge } from "@/components/ui";
import { StageProgress } from "@/components/StageProgress";
import { ViralDnaReport } from "@/components/ViralDnaReport";
import { ConceptPicker } from "@/components/ConceptPicker";
import { ScriptControlsForm } from "@/components/ScriptControlsForm";
import { ScriptResult } from "@/components/ScriptResult";
import { OriginalityPanel } from "@/components/OriginalityPanel";
import { HowToMakeVideo } from "@/components/HowToMakeVideo";

const ANALYSIS_TERMINAL = ["AWAITING_CONCEPT_SELECTION", "FAILED", "COMPLETED"];
const SCRIPT_TERMINAL = ["COMPLETED", "FAILED"];
const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

function SectionTitle({ n, title, sub }: { n: string; title: string; sub?: string }) {
  return (
    <div className="mb-4 flex items-baseline gap-3">
      <span className="font-mono text-sm text-accent">{n}</span>
      <div>
        <h2 className="text-xl font-semibold tracking-tight">{title}</h2>
        {sub && <p className="text-sm text-muted">{sub}</p>}
      </div>
    </div>
  );
}

export default function AnalysisWorkspace({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { user: authUser, loading: authLoading } = useRequireAuth();
  const [analysis, setAnalysis] = useState<AnalysisView | null>(null);
  const [scriptView, setScriptView] = useState<ScriptView | null>(null);
  const [selected, setSelected] = useState<number | null>(null);
  const [generating, setGenerating] = useState(false);
  const [rewriting, setRewriting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [outOfCredits, setOutOfCredits] = useState(false);
  const alive = useRef(true);

  useEffect(() => {
    alive.current = true;
    return () => { alive.current = false; };
  }, []);

  // Poll the analysis job until it settles.
  useEffect(() => {
    if (authLoading) return;
    if (supabaseEnabled && !authUser) return;
    async function tick() {
      try {
        const a = await api.getAnalysis(id);
        if (!alive.current) return;
        setAnalysis(a);
        if (ANALYSIS_TERMINAL.includes(a.status)) {
          const s = await api.getScript(id).catch(() => null);
          if (alive.current && s) {
            setScriptView(s);
            if (s.concept_index !== null) setSelected(s.concept_index);
          }
          return;
        }
      } catch (e) {
        if (alive.current) setError(e instanceof ApiError ? e.message : "Failed to load analysis");
        return;
      }
      if (alive.current) setTimeout(tick, 900);
    }
    tick();
  }, [id, authLoading, authUser]);

  const generate = useCallback(
    async (controls: Partial<ScriptControls>) => {
      if (selected === null) return;
      setGenerating(true);
      setError(null);
      setOutOfCredits(false);
      try {
        await api.startScript(id, selected, controls);
        while (alive.current) {
          const s = await api.getScript(id);
          if (!alive.current) break;
          setScriptView(s);
          if (!s.status || SCRIPT_TERMINAL.includes(s.status)) break;
          await sleep(900);
        }
      } catch (e) {
        if (e instanceof ApiError && e.status === 402) setOutOfCredits(true);
        else setError(e instanceof ApiError ? e.message : "Script generation failed");
      } finally {
        if (alive.current) setGenerating(false);
      }
    },
    [id, selected],
  );

  const rewrite = useCallback(async () => {
    if (!scriptView?.script_id) return;
    setRewriting(true);
    try {
      await api.rewrite(scriptView.script_id, "flagged");
      // Rewrite runs as a background job and keeps status COMPLETED; refetch a few times.
      for (let i = 0; i < 5 && alive.current; i++) {
        await sleep(800);
        const s = await api.getScript(id);
        if (alive.current) setScriptView(s);
      }
    } finally {
      if (alive.current) setRewriting(false);
    }
  }, [id, scriptView?.script_id]);

  const analysisDone = analysis?.status === "AWAITING_CONCEPT_SELECTION";
  const analysisFailed = analysis?.status === "FAILED";
  const scriptStatus = scriptView?.status ?? null;
  const scriptDone = scriptStatus === "COMPLETED";

  if (authLoading)
    return (
      <div className="grid min-h-screen place-items-center bg-background">
        <Spinner className="h-6 w-6" />
      </div>
    );
  if (supabaseEnabled && !authUser) return null;

  return (
    <>
      <TopNav />
      <main className="mx-auto max-w-5xl px-5 py-8">
        <div className="mb-6 flex items-center justify-between">
          <Link href="/dashboard" className="text-sm text-muted hover:text-foreground">← Dashboard</Link>
          <StatusBadge status={analysis?.status} />
        </div>

        {/* Source */}
        {analysis?.source_video && (
          <Card className="mb-6 flex flex-wrap items-center justify-between gap-3">
            <div className="min-w-0">
              <div className="text-xs uppercase tracking-wide text-muted-2">Source video</div>
              <div className="truncate font-medium">{analysis.source_video.title || analysis.source_video.url}</div>
              <div className="text-xs text-muted-2">
                {analysis.source_video.channel_name} · {analysis.source_video.platform}
              </div>
            </div>
            <a href={analysis.source_video.url} target="_blank" rel="noreferrer">
              <Badge>Open original ↗</Badge>
            </a>
          </Card>
        )}

        {error && <Card className="mb-6 border-danger/30 text-danger">{error}</Card>}

        {/* Analysis progress */}
        {!analysisDone && !analysisFailed && (
          <Card className="mb-6 space-y-4">
            <SectionTitle n="01" title="Analyzing the source" sub={analysis?.stage || "Starting…"} />
            <StageProgress status={analysis?.status ?? null} kind="analysis" done={false} />
          </Card>
        )}
        {analysisFailed && (
          <Card className="mb-6 border-danger/30">
            <div className="font-medium text-danger">Analysis failed</div>
            <p className="text-sm text-muted">{analysis?.error_reason}</p>
          </Card>
        )}

        {/* Viral DNA */}
        {analysis?.viral_dna && (
          <section className="mb-10">
            <SectionTitle n="02" title="Viral DNA" sub="Why this video works — mechanics, not wording." />
            <ViralDnaReport dna={analysis.viral_dna} />
          </section>
        )}

        {/* Concepts */}
        {analysis?.concepts && (
          <section className="mb-10">
            <SectionTitle
              n="03"
              title="Original concepts"
              sub="Divergent angles that reuse the mechanics. Pick one to script."
            />
            <ConceptPicker
              concepts={analysis.concepts.concepts}
              selected={selected}
              onSelect={setSelected}
              disabled={generating || scriptDone}
            />
          </section>
        )}

        {/* Script generation */}
        {analysis?.concepts && (
          <section className="mb-10">
            <SectionTitle n="04" title="Original script" sub="Grounded in a fresh angle, audited for originality." />
            {!scriptDone && (
              <ScriptControlsForm disabled={selected === null || generating} generating={generating} onGenerate={generate} />
            )}

            {outOfCredits && !scriptDone && (
              <Card className="mt-4 border-warning/40 bg-warning/5">
                <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <div className="font-medium text-amber-200">You&apos;re out of credits</div>
                    <p className="mt-0.5 text-sm text-muted">
                      Each script generation (including regenerating from another concept) uses 1 credit. Refill to keep going, or upgrade your plan.
                    </p>
                  </div>
                  <div className="flex shrink-0 gap-2">
                    <Button size="sm" onClick={() => startCheckout("creator")}>Upgrade to Creator</Button>
                    <Button variant="outline" size="sm" onClick={async () => { await api.refillCredits(50); setOutOfCredits(false); }}>Refill (dev)</Button>
                  </div>
                </div>
              </Card>
            )}

            {generating && !scriptDone && (
              <Card className="mt-4">
                <StageProgress status={scriptStatus} kind="script" done={false} />
              </Card>
            )}

            {scriptView?.status === "FAILED" && (
              <Card className="mt-4 border-danger/30 text-danger">
                Script generation failed: {scriptView.error_reason}
              </Card>
            )}

            {scriptDone && scriptView?.script && (
              <div className="mt-4 grid gap-4 lg:grid-cols-5">
                <div className="space-y-4 lg:col-span-3">
                  <ScriptResult projectId={id} script={scriptView.script} pkg={scriptView.production_package} />
                  <HowToMakeVideo pkg={scriptView.production_package} originality={scriptView.originality_report} />
                </div>
                <div className="lg:col-span-2">
                  {scriptView.originality_report && (
                    <OriginalityPanel report={scriptView.originality_report} onRewrite={rewrite} rewriting={rewriting} />
                  )}
                  <div className="mt-4">
                    <Button variant="outline" size="sm" onClick={() => { setScriptView(null); setSelected(selected); }}>
                      ← Regenerate from another concept
                    </Button>
                  </div>
                </div>
              </div>
            )}
          </section>
        )}
      </main>
    </>
  );
}
