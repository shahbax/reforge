import type { JobStatus } from "@/lib/types";
import { Spinner } from "./ui";

const ANALYSIS_STAGES: { key: JobStatus; label: string }[] = [
  { key: "DOWNLOADING", label: "Fetch video" },
  { key: "TRANSCRIBING", label: "Transcript" },
  { key: "ANALYZING", label: "Analyze" },
  { key: "GENERATING_CONCEPTS", label: "Concepts" },
];

const SCRIPT_STAGES: { key: JobStatus; label: string }[] = [
  { key: "RESEARCHING", label: "Research" },
  { key: "GENERATING_SCRIPT", label: "Write script" },
  { key: "CHECKING_ORIGINALITY", label: "Originality" },
];

function order(kind: "analysis" | "script") {
  return kind === "analysis" ? ANALYSIS_STAGES : SCRIPT_STAGES;
}

export function StageProgress({
  status,
  kind,
  done,
  failed,
}: {
  status: JobStatus | null;
  kind: "analysis" | "script";
  done: boolean;
  failed?: boolean;
}) {
  const stages = order(kind);
  const currentIdx = status ? stages.findIndex((s) => s.key === status) : -1;

  return (
    <div className="flex flex-wrap items-center gap-x-2 gap-y-3">
      {stages.map((s, i) => {
        const complete = done || (currentIdx > -1 && i < currentIdx);
        const active = !done && i === currentIdx;
        return (
          <div key={s.key} className="flex items-center gap-2">
            <div
              className={[
                "flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs",
                complete
                  ? "border-success/30 bg-success/10 text-emerald-300"
                  : active
                    ? "border-accent/40 bg-accent/10 text-violet-200"
                    : failed
                      ? "border-danger/30 bg-danger/5 text-red-300/70"
                      : "border-line bg-surface text-muted-2",
              ].join(" ")}
            >
              {complete ? <span>✓</span> : active ? <Spinner className="h-3 w-3" /> : <span className="opacity-50">○</span>}
              {s.label}
            </div>
            {i < stages.length - 1 && <span className="text-muted-2">→</span>}
          </div>
        );
      })}
    </div>
  );
}
