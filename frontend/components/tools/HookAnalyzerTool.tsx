"use client";

import { useState } from "react";
import { api, ApiError } from "@/lib/api";
import type { HookResult } from "@/lib/types";
import { Badge, Button, Card, Spinner } from "@/components/ui";

function color(s: number) {
  return s >= 70 ? "var(--success)" : s >= 45 ? "var(--warning)" : "var(--danger)";
}

export function HookAnalyzerTool() {
  const [text, setText] = useState("");
  const [result, setResult] = useState<HookResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function run() {
    setError(null);
    setBusy(true);
    try {
      setResult(await api.hookTool(text));
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Something went wrong");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-4">
      <div>
        <label className="mb-1.5 block text-sm font-medium">Your hook (the first line of your video)</label>
        <textarea
          className="min-h-28 w-full rounded-lg border border-line bg-surface-solid p-3 text-sm text-foreground placeholder:text-muted-2 focus:border-accent/60 focus:outline-none focus:ring-2 focus:ring-accent/20"
          placeholder="e.g. You're making this one mistake every single day and never notice it…"
          value={text}
          onChange={(e) => setText(e.target.value)}
        />
      </div>
      <Button size="lg" onClick={run} disabled={busy || !text.trim()}>
        {busy ? <><Spinner /> Analyzing…</> : "Analyze hook →"}
      </Button>
      {error && <p className="text-sm text-danger">{error}</p>}

      {result && (
        <Card className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-xs uppercase tracking-wide text-muted-2">Hook type</div>
              <div className="text-lg font-semibold">{result.hook_type}</div>
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold" style={{ color: color(result.strength) }}>{result.strength}</div>
              <div className="text-xs text-muted-2">strength</div>
            </div>
          </div>
          <div className="flex flex-wrap gap-2">
            <Badge tone={result.has_question ? "success" : "neutral"}>{result.has_question ? "Has a question" : "No question"}</Badge>
            <Badge tone={result.addresses_viewer ? "success" : "neutral"}>{result.addresses_viewer ? "Speaks to viewer" : "Not personal"}</Badge>
            <Badge tone={result.curiosity_markers > 0 ? "success" : "neutral"}>{result.curiosity_markers} curiosity markers</Badge>
            <Badge>{result.length_words} words</Badge>
          </div>
          <div>
            <div className="mb-1.5 text-sm font-medium">Suggestions</div>
            <ul className="space-y-1">
              {result.suggestions.map((s, i) => (
                <li key={i} className="flex gap-2 text-sm text-muted"><span className="text-accent">•</span>{s}</li>
              ))}
            </ul>
          </div>
        </Card>
      )}
    </div>
  );
}
