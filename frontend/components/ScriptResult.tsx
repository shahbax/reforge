"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import type { ProductionPackage, Script } from "@/lib/types";
import { Badge, Button, Card } from "./ui";

function CopyButton({ text, label = "Copy", size = "sm" as const }: { text: string; label?: string; size?: "sm" }) {
  const [done, setDone] = useState(false);
  return (
    <Button
      variant="ghost"
      size={size}
      onClick={async () => { await navigator.clipboard.writeText(text); setDone(true); setTimeout(() => setDone(false), 1400); }}
    >
      {done ? "Copied ✓" : label}
    </Button>
  );
}

export function ScriptResult({
  projectId,
  script,
  pkg,
}: {
  projectId: string;
  script: Script;
  pkg: ProductionPackage | null;
}) {
  const readMin = Math.max(1, Math.round(script.word_count / 150));

  return (
    <div className="space-y-4">
      <Card className="glass fade-up space-y-4 p-6">
        <div className="flex flex-wrap items-start justify-between gap-3 border-b border-line pb-4">
          <div className="min-w-0">
            <div className="mb-1 flex items-center gap-2">
              <span className="grid h-6 w-6 place-items-center rounded-md bg-gradient-to-br from-violet-500 to-cyan-400 text-[11px] font-bold text-black">VR</span>
              <span className="text-[11px] uppercase tracking-wide text-muted-2">Your original script</span>
            </div>
            <h3 className="text-xl font-semibold leading-snug">{script.title}</h3>
            <p className="mt-1 text-xs text-muted-2">{script.word_count} words · ~{readMin} min read · {script.sections.length} sections</p>
          </div>
          <div className="flex items-center gap-1.5">
            <CopyButton text={script.full_text} label="Copy script" />
            <Button onClick={() => api.exportScript(projectId, "md")} variant="outline" size="sm">.md</Button>
            <Button onClick={() => api.exportScript(projectId, "txt")} variant="ghost" size="sm">.txt</Button>
          </div>
        </div>

        <div className="space-y-3">
          {script.sections.map((s, i) => (
            <div key={i} className="group relative rounded-xl border border-line bg-surface-solid/60 p-4">
              <div className="mb-1.5 flex items-center justify-between">
                <span className="rounded-md border border-accent/25 bg-accent/10 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-violet-200">
                  {s.label}
                </span>
                <span className="opacity-0 transition-opacity group-hover:opacity-100">
                  <CopyButton text={s.content} />
                </span>
              </div>
              <p className="text-[15px] leading-relaxed text-foreground/90">{s.content}</p>
            </div>
          ))}
        </div>
      </Card>

      {pkg && (
        <Card className="fade-up space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold">Production package</h3>
            <Badge tone="accent">ready to publish</Badge>
          </div>
          {pkg.titles.length > 0 && (
            <div>
              <div className="mb-1.5 text-xs uppercase tracking-wide text-muted-2">Title options</div>
              <ul className="space-y-1.5">
                {pkg.titles.map((t, i) => (
                  <li key={i} className="group flex items-center justify-between gap-2 rounded-lg border border-line bg-surface-solid/50 px-3 py-2 text-sm text-foreground/90">
                    <span className="min-w-0 truncate">{t}</span>
                    <span className="shrink-0 opacity-0 transition-opacity group-hover:opacity-100"><CopyButton text={t} /></span>
                  </li>
                ))}
              </ul>
            </div>
          )}
          {pkg.description && (
            <div>
              <div className="mb-1 flex items-center justify-between">
                <span className="text-xs uppercase tracking-wide text-muted-2">Description</span>
                <CopyButton text={pkg.description} />
              </div>
              <p className="text-sm text-muted">{pkg.description}</p>
            </div>
          )}
          {pkg.thumbnail_prompts.length > 0 && (
            <div>
              <div className="mb-1.5 text-xs uppercase tracking-wide text-muted-2">Thumbnail prompts</div>
              <ul className="space-y-1 text-sm text-muted">
                {pkg.thumbnail_prompts.map((t, i) => <li key={i}>• {t}</li>)}
              </ul>
            </div>
          )}
          {pkg.hashtags.length > 0 && (
            <div>
              <div className="mb-1.5 text-xs uppercase tracking-wide text-muted-2">Hashtags</div>
              <div className="flex flex-wrap gap-1.5">
                {pkg.hashtags.map((h, i) => <Badge key={i}>{h}</Badge>)}
              </div>
            </div>
          )}
        </Card>
      )}
    </div>
  );
}
