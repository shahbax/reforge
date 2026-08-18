"use client";

import { useState } from "react";
import type { Platform, ScriptControls } from "@/lib/types";
import { Button, Card, Field, Select, Spinner } from "./ui";

export function ScriptControlsForm({
  disabled,
  generating,
  onGenerate,
}: {
  disabled: boolean;
  generating: boolean;
  onGenerate: (c: Partial<ScriptControls>) => void;
}) {
  const [platform, setPlatform] = useState<Platform>("youtube");
  const [tone, setTone] = useState("engaging");
  const [duration, setDuration] = useState(180);
  const [language, setLanguage] = useState("en");
  const [style, setStyle] = useState("narrative");
  const [research, setResearch] = useState<"light" | "standard" | "deep">("standard");
  const [cta, setCta] = useState("subscribe");

  return (
    <Card className="space-y-4">
      <div>
        <h3 className="text-lg font-semibold">Script controls</h3>
        <p className="text-xs text-muted-2">
          {disabled ? "Select a concept above to configure the script." : "Tune the output, then generate."}
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <Field label="Platform">
          <Select value={platform} onChange={(e) => setPlatform(e.target.value as Platform)} disabled={disabled}>
            <option value="youtube">YouTube</option>
            <option value="tiktok">TikTok</option>
            <option value="instagram">Instagram</option>
          </Select>
        </Field>
        <Field label="Tone">
          <Select value={tone} onChange={(e) => setTone(e.target.value)} disabled={disabled}>
            {["engaging", "curious", "authoritative", "conversational", "energetic", "calm"].map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </Select>
        </Field>
        <Field label="Duration" hint={`~${Math.max(80, Math.round((duration / 60) * 150))} words`}>
          <Select value={duration} onChange={(e) => setDuration(Number(e.target.value))} disabled={disabled}>
            <option value={60}>60 seconds (Short)</option>
            <option value={180}>3 minutes</option>
            <option value={300}>5 minutes</option>
            <option value={600}>10 minutes</option>
          </Select>
        </Field>
        <Field label="Storytelling style">
          <Select value={style} onChange={(e) => setStyle(e.target.value)} disabled={disabled}>
            {["narrative", "listicle", "explainer", "case-study", "essay"].map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </Select>
        </Field>
        <Field label="Research depth">
          <Select value={research} onChange={(e) => setResearch(e.target.value as "light" | "standard" | "deep")} disabled={disabled}>
            <option value="light">Light</option>
            <option value="standard">Standard</option>
            <option value="deep">Deep</option>
          </Select>
        </Field>
        <Field label="CTA style">
          <Select value={cta} onChange={(e) => setCta(e.target.value)} disabled={disabled}>
            {["subscribe", "comment", "follow", "soft-ask", "none"].map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </Select>
        </Field>
      </div>

      <Button
        disabled={disabled || generating}
        onClick={() =>
          onGenerate({
            platform,
            tone,
            duration_seconds: duration,
            language,
            storytelling_style: style,
            research_level: research,
            cta_style: cta,
          })
        }
        className="w-full"
        size="lg"
      >
        {generating ? <><Spinner /> Generating script…</> : "Generate original script →"}
      </Button>
    </Card>
  );
}
