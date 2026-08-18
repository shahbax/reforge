const STAGES = [
  { n: "01", t: "Ingest & transcribe", d: "Paste any YouTube URL — we pull the transcript and metadata. No re-watching.", accent: false },
  { n: "02", t: "Extract the Viral DNA", d: "Explainable mechanics: hook type, emotional arc, open loops, retention.", accent: false },
  { n: "03", t: "Generate original concepts", d: "5–10 divergent angles engineered to reuse mechanics, not wording.", accent: false },
  { n: "04", t: "Write the original script", d: "A research-grounded, ready-to-film script in your niche and tone.", accent: false },
  { n: "05", t: "Originality Guard", d: "Source-vs-generated similarity audit + score — so it isn't derivative.", accent: true },
];

export function PipelineStack() {
  return (
    <div className="relative mx-auto max-w-2xl">
      {STAGES.map((s, i) => (
        <div
          key={s.n}
          className={[
            "group relative rounded-2xl border p-5 transition-transform hover:-translate-y-1",
            s.accent
              ? "border-accent/40 bg-gradient-to-br from-accent/15 to-transparent"
              : "border-line bg-surface",
          ].join(" ")}
          style={{
            marginTop: i === 0 ? 0 : -14,
            marginLeft: `${i * 18}px`,
            marginRight: `${(STAGES.length - 1 - i) * 18}px`,
            zIndex: i + 1,
            boxShadow: "0 20px 40px -24px rgba(0,0,0,0.7)",
          }}
        >
          <div className="flex items-center gap-4">
            <span
              className={[
                "grid h-10 w-10 shrink-0 place-items-center rounded-xl font-mono text-sm font-semibold",
                s.accent ? "bg-accent text-white" : "bg-surface-solid text-accent",
              ].join(" ")}
            >
              {s.n}
            </span>
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <h3 className="font-semibold">{s.t}</h3>
                {s.accent && (
                  <span className="rounded-full border border-accent/30 bg-accent/15 px-2 py-0.5 text-[10px] font-medium text-violet-200">
                    only in Reforge
                  </span>
                )}
              </div>
              <p className="mt-0.5 text-sm text-muted">{s.d}</p>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
