"use client";

import { useState } from "react";
import { api, ApiError } from "@/lib/api";
import type { TranscriptResult } from "@/lib/types";
import { Badge, Button, Card, Spinner, TextInput } from "@/components/ui";

export function TranscriptExtractorTool() {
  const [url, setUrl] = useState("");
  const [result, setResult] = useState<TranscriptResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  async function run() {
    setError(null);
    setBusy(true);
    setResult(null);
    try {
      setResult(await api.transcriptTool(url.trim()));
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Something went wrong");
    } finally {
      setBusy(false);
    }
  }

  async function copy() {
    if (!result) return;
    await navigator.clipboard.writeText(result.transcript);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  return (
    <div className="space-y-4">
      <form onSubmit={(e) => { e.preventDefault(); run(); }} className="flex flex-col gap-3 sm:flex-row">
        <TextInput type="url" required placeholder="https://www.youtube.com/watch?v=…" value={url} onChange={(e) => setUrl(e.target.value)} className="flex-1" />
        <Button type="submit" disabled={busy || !url.trim()}>{busy ? <><Spinner /> Extracting…</> : "Get transcript →"}</Button>
      </form>
      {error && <p className="text-sm text-danger">{error}</p>}

      {result && (
        <Card className="space-y-3">
          <div className="flex items-start justify-between gap-3">
            <div>
              <div className="font-medium">{result.title || "Transcript"}</div>
              <div className="text-xs text-muted-2">
                {result.channel && `${result.channel} · `}{result.word_count} words · source: {result.source}
              </div>
            </div>
            <Button variant="outline" size="sm" onClick={copy}>{copied ? "Copied ✓" : "Copy"}</Button>
          </div>
          {result.source === "mock" && (
            <p className="rounded-lg border border-warning/25 bg-warning/5 p-2.5 text-xs text-amber-200">
              Demo mode: showing a sample transcript. Real caption extraction turns on once the server has ingestion configured.
            </p>
          )}
          <div className="max-h-96 overflow-y-auto whitespace-pre-wrap rounded-lg border border-line bg-surface-solid p-3 text-sm text-foreground/90">
            {result.transcript}
          </div>
        </Card>
      )}
    </div>
  );
}
