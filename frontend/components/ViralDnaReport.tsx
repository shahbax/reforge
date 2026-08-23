import type { ViralDNA } from "@/lib/types";
import { Badge, Card, Chips, InfoTip } from "./ui";

// Plain-language definitions for the jargon, shown on hover for beginners.
const TIPS: Record<string, string> = {
  Hook: "The opening line/idea that grabs attention in the first few seconds and makes people keep watching.",
  "Open loops": "Questions or mysteries opened early and deliberately left unanswered, so viewers stay to get the payoff.",
  "Pattern interrupts": "Small changes (a cut, a question, a visual) that reset attention so viewers don't scroll away.",
  "Reusable principles": "The transferable lessons you can reuse in your own original video — the safe, non-copying takeaways.",
  "Emotional progression": "The sequence of feelings the video walks viewers through, from the hook to the payoff.",
  "Narrative structure": "The order the video tells its story in — the beat-by-beat skeleton you can adapt.",
  "Retention hypotheses": "Our best guesses for why viewers kept watching — the mechanics driving watch time.",
};

function List({ title, items }: { title: string; items: string[] }) {
  if (!items?.length) return null;
  return (
    <div>
      <div className="mb-1.5 text-xs font-medium uppercase tracking-wide text-muted-2">
        {title}
        {TIPS[title] && <InfoTip text={TIPS[title]} />}
      </div>
      <ul className="space-y-1">
        {items.map((it, i) => (
          <li key={i} className="flex gap-2 text-sm text-foreground">
            <span className="text-accent">•</span>
            <span>{it}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function Fact({ label, value }: { label: string; value: string }) {
  if (!value) return null;
  return (
    <div>
      <div className="text-xs uppercase tracking-wide text-muted-2">{label}</div>
      <div className="text-sm text-foreground">{value}</div>
    </div>
  );
}

export function ViralDnaReport({ dna }: { dna: ViralDNA }) {
  return (
    <div className="space-y-4">
      {/* Hook spotlight */}
      <Card className="glass fade-up border-accent/25 bg-gradient-to-br from-accent/10 to-transparent">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <div className="text-xs uppercase tracking-wide text-muted-2">
              Hook<InfoTip text={TIPS.Hook} />
            </div>
            <div className="mt-0.5 text-lg font-semibold">{dna.hook.type}</div>
            <p className="mt-1 max-w-xl text-sm text-muted">{dna.hook.curiosity_mechanism}</p>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold text-gradient">{dna.hook.strength}</div>
            <div className="text-xs text-muted-2">hook strength</div>
          </div>
        </div>
        <div className="mt-3 h-1.5 w-full overflow-hidden rounded-full bg-surface-solid">
          <div
            className="h-full rounded-full bg-gradient-to-r from-violet-500 to-cyan-400"
            style={{ width: `${Math.max(0, Math.min(100, dna.hook.strength))}%` }}
          />
        </div>
      </Card>

      <div className="grid gap-4 md:grid-cols-2">
        <Card className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <Fact label="Niche" value={dna.niche} />
            <Fact label="Archetype" value={dna.content_archetype} />
            <Fact label="Topic" value={dna.topic} />
            <Fact label="Audience" value={dna.target_audience} />
            <Fact label="Information density" value={dna.information_density} />
            <Fact label="Pacing" value={dna.pacing} />
          </div>
          <Fact label="Story arc" value={dna.story_arc} />
          <div>
            <div className="mb-1.5 text-xs uppercase tracking-wide text-muted-2">
              Emotional progression<InfoTip text={TIPS["Emotional progression"]} />
            </div>
            <div className="flex flex-wrap items-center gap-1.5">
              {dna.emotional_progression.map((e, i) => (
                <span key={i} className="flex items-center gap-1.5">
                  <Badge tone="accent">{e}</Badge>
                  {i < dna.emotional_progression.length - 1 && <span className="text-muted-2">→</span>}
                </span>
              ))}
            </div>
          </div>
        </Card>

        <Card className="space-y-3">
          <div>
            <div className="mb-1.5 text-xs uppercase tracking-wide text-muted-2">
              Narrative structure<InfoTip text={TIPS["Narrative structure"]} />
            </div>
            <Chips items={dna.narrative_structure} tone="accent" />
          </div>
          <List title="Open loops" items={dna.open_loops} />
          <List title="Payoff points" items={dna.payoff_points} />
          <List title="Escalation points" items={dna.escalation_points} />
        </Card>

        <Card className="space-y-3">
          <List title="Why it worked" items={dna.why_it_worked} />
          <List title="Retention hypotheses" items={dna.retention_hypotheses} />
        </Card>

        <Card className="space-y-3">
          <List title="Reusable principles" items={dna.reusable_principles} />
          <List title="Pattern interrupts" items={dna.pattern_interrupts} />
          <Fact label="CTA strategy" value={dna.cta_strategy} />
          <Fact label="Title strategy" value={dna.title_strategy} />
        </Card>
      </div>
    </div>
  );
}
