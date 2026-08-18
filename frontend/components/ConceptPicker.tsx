import type { Concept } from "@/lib/types";
import { Chips } from "./ui";

export function ConceptPicker({
  concepts,
  selected,
  onSelect,
  disabled,
}: {
  concepts: Concept[];
  selected: number | null;
  onSelect: (i: number) => void;
  disabled?: boolean;
}) {
  return (
    <div className="grid gap-3 md:grid-cols-2">
      {concepts.map((c, i) => {
        const active = selected === i;
        return (
          <button
            key={i}
            onClick={() => !disabled && onSelect(i)}
            disabled={disabled}
            className={[
              "flex flex-col gap-2 rounded-xl border p-4 text-left transition-all",
              active
                ? "border-accent bg-accent/10 ring-1 ring-accent/40"
                : "border-line bg-surface hover:border-line-strong",
              disabled ? "cursor-not-allowed opacity-60" : "cursor-pointer",
            ].join(" ")}
          >
            <div className="flex items-start justify-between gap-2">
              <h4 className="font-semibold leading-snug">{c.title}</h4>
              <span
                className={[
                  "mt-0.5 grid h-5 w-5 shrink-0 place-items-center rounded-full border text-xs",
                  active ? "border-accent bg-accent text-white" : "border-line-strong text-transparent",
                ].join(" ")}
              >
                ✓
              </span>
            </div>
            <p className="text-sm text-muted">{c.premise}</p>
            <div className="text-xs">
              <span className="text-muted-2">Angle: </span>
              <span className="text-foreground">{c.unique_angle}</span>
            </div>
            <div className="rounded-lg border border-line bg-surface-solid p-2 text-xs text-muted">
              <span className="text-accent">Hook — </span>
              {c.hook}
            </div>
            <div className="text-xs">
              <span className="text-muted-2">Differs from source: </span>
              <span className="text-foreground">{c.how_it_differs_from_source}</span>
            </div>
            {c.suggested_structure?.length > 0 && <Chips items={c.suggested_structure} />}
          </button>
        );
      })}
    </div>
  );
}
