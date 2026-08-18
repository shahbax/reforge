import { api } from "@/lib/api";
import type { ProductionPackage, Script } from "@/lib/types";
import { Badge, Button, Card, Chips } from "./ui";

export function ScriptResult({
  projectId,
  script,
  pkg,
}: {
  projectId: string;
  script: Script;
  pkg: ProductionPackage | null;
}) {
  return (
    <div className="space-y-4">
      <Card className="space-y-4">
        <div className="flex items-start justify-between gap-3">
          <div>
            <h3 className="text-lg font-semibold">{script.title}</h3>
            <p className="text-xs text-muted-2">{script.word_count} words</p>
          </div>
          <div className="flex gap-2">
            <Button href={api.exportUrl(projectId, "md")} variant="outline" size="sm">Export .md</Button>
            <Button href={api.exportUrl(projectId, "txt")} variant="ghost" size="sm">.txt</Button>
          </div>
        </div>
        <div className="space-y-3">
          {script.sections.map((s, i) => (
            <div key={i} className="rounded-lg border border-line bg-surface-solid p-3">
              <div className="mb-1 text-xs font-medium uppercase tracking-wide text-accent">{s.label}</div>
              <p className="text-sm leading-relaxed text-foreground/90">{s.content}</p>
            </div>
          ))}
        </div>
      </Card>

      {pkg && (
        <Card className="space-y-3">
          <h3 className="font-semibold">Production package</h3>
          {pkg.titles.length > 0 && (
            <div>
              <div className="mb-1.5 text-xs uppercase tracking-wide text-muted-2">Title options</div>
              <ul className="space-y-1 text-sm">
                {pkg.titles.map((t, i) => <li key={i} className="text-foreground/90">{t}</li>)}
              </ul>
            </div>
          )}
          {pkg.description && (
            <div>
              <div className="mb-1 text-xs uppercase tracking-wide text-muted-2">Description</div>
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
