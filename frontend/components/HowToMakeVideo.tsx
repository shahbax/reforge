import type { OriginalityReport, ProductionPackage } from "@/lib/types";
import { Card } from "./ui";

export function HowToMakeVideo({
  pkg,
  originality,
}: {
  pkg: ProductionPackage | null;
  originality: OriginalityReport | null;
}) {
  const steps = [
    {
      t: "Record the voiceover",
      d: "Read the script above aloud, or paste it into a text-to-speech tool. Keep the hook punchy — the first 5 seconds decide whether viewers stay.",
    },
    {
      t: "Add visuals & b-roll",
      d: "Layer stock footage, screen recordings, or simple motion graphics over the voiceover so each section has something to watch.",
    },
    {
      t: "Pick your title",
      d: pkg?.titles?.length
        ? `Use one of the generated titles, e.g. “${pkg.titles[0]}”.`
        : "Choose a curiosity-driven title with a concrete noun.",
    },
    {
      t: "Design the thumbnail",
      d: pkg?.thumbnail_prompts?.length
        ? `Use a thumbnail prompt, e.g. “${pkg.thumbnail_prompts[0]}”.`
        : "Single subject, high contrast, a small curiosity cue.",
    },
    {
      t: "Check originality before publishing",
      d: originality
        ? `Your originality score is ${originality.originality_score}/100 — higher is safer against YouTube's reused / inauthentic-content flags. Rewrite any flagged passages first.`
        : "Keep your script original and varied before publishing.",
    },
  ];

  return (
    <Card className="space-y-3">
      <div>
        <h3 className="font-semibold">How to make this video</h3>
        <p className="text-xs text-muted-2">New to this? Follow these steps to go from script to a published video.</p>
      </div>
      <ol className="space-y-2.5">
        {steps.map((s, i) => (
          <li key={i} className="flex gap-3">
            <span className="grid h-6 w-6 shrink-0 place-items-center rounded-full bg-accent/15 text-xs font-semibold text-violet-300">
              {i + 1}
            </span>
            <div>
              <div className="text-sm font-medium">{s.t}</div>
              <div className="text-sm text-muted">{s.d}</div>
            </div>
          </li>
        ))}
      </ol>
    </Card>
  );
}
