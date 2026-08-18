"use client";

import { useEffect, useRef, useState } from "react";

function useCountUp(target: number, run: boolean, ms = 1200) {
  const [v, setV] = useState(0);
  useEffect(() => {
    if (!run) return;
    let raf = 0;
    const start = performance.now();
    const tick = (now: number) => {
      const p = Math.min(1, (now - start) / ms);
      const eased = 1 - Math.pow(1 - p, 3);
      setV(Math.round(eased * target));
      if (p < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [target, run, ms]);
  return v;
}

function ScoreRing({ score }: { score: number }) {
  const r = 34;
  const c = 2 * Math.PI * r;
  return (
    <div className="relative h-24 w-24">
      <svg viewBox="0 0 80 80" className="h-full w-full -rotate-90">
        <circle cx="40" cy="40" r={r} fill="none" stroke="var(--line)" strokeWidth="6" />
        <circle
          cx="40" cy="40" r={r} fill="none" stroke="var(--success)" strokeWidth="6" strokeLinecap="round"
          strokeDasharray={c} strokeDashoffset={c * (1 - score / 100)}
          style={{ transition: "stroke-dashoffset 1.2s cubic-bezier(0.16,1,0.3,1)" }}
        />
      </svg>
      <div className="absolute inset-0 grid place-items-center">
        <div className="text-center">
          <div className="text-2xl font-bold text-emerald-400">{score}</div>
          <div className="text-[9px] uppercase tracking-wide text-muted-2">original</div>
        </div>
      </div>
    </div>
  );
}

const HOOK_LINE = "You repeat this 40 times a week and never notice what it does.";

export function HeroPreview() {
  const ref = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(false);
  const [typed, setTyped] = useState("");
  const score = useCountUp(87, visible);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const io = new IntersectionObserver(([e]) => e.isIntersecting && setVisible(true), { threshold: 0.3 });
    io.observe(el);
    return () => io.disconnect();
  }, []);

  useEffect(() => {
    if (!visible) return;
    let i = 0;
    const id = setInterval(() => {
      i += 1;
      setTyped(HOOK_LINE.slice(0, i));
      if (i >= HOOK_LINE.length) clearInterval(id);
    }, 28);
    return () => clearInterval(id);
  }, [visible]);

  return (
    <div ref={ref} className="floaty glass rounded-2xl p-4 text-left">
      {/* window chrome */}
      <div className="mb-3 flex items-center gap-2 border-b border-line pb-3">
        <span className="h-2.5 w-2.5 rounded-full bg-red-400/70" />
        <span className="h-2.5 w-2.5 rounded-full bg-amber-400/70" />
        <span className="h-2.5 w-2.5 rounded-full bg-emerald-400/70" />
        <div className="ml-2 flex-1 truncate rounded-md bg-surface-solid px-2 py-1 text-xs text-muted-2">
          reforge.app/analysis — youtube.com/watch?v=…
        </div>
      </div>

      <div className="grid gap-3 sm:grid-cols-5">
        {/* Viral DNA */}
        <div className="sm:col-span-3 space-y-3">
          <div className="rounded-xl border border-accent/25 bg-accent/5 p-3">
            <div className="text-[10px] uppercase tracking-wide text-muted-2">Hook</div>
            <div className="text-sm font-semibold">contradiction / unanswered question</div>
            <div className="mt-1 flex flex-wrap items-center gap-1 text-[11px]">
              {["curiosity", "confusion", "surprise", "revelation"].map((e, i) => (
                <span key={e} className="flex items-center gap-1">
                  <span className="rounded-md border border-accent/25 bg-accent/10 px-1.5 py-0.5 text-violet-200">{e}</span>
                  {i < 3 && <span className="text-muted-2">→</span>}
                </span>
              ))}
            </div>
          </div>
          <div className="rounded-xl border border-line bg-surface-solid p-3">
            <div className="text-[10px] uppercase tracking-wide text-muted-2">Original script · Hook</div>
            <p className="mt-1 text-sm text-foreground/90">
              {typed}
              <span className="blink text-accent">▌</span>
            </p>
          </div>
        </div>

        {/* Originality */}
        <div className="sm:col-span-2 flex flex-col items-center justify-center rounded-xl border border-line bg-surface-solid p-3">
          <ScoreRing score={score} />
          <div className="mt-2 text-center text-[11px] text-muted">Originality Guard</div>
          <div className="mt-1 flex flex-wrap justify-center gap-1 text-[9px]">
            {["phrase LOW", "semantic LOW"].map((b) => (
              <span key={b} className="rounded-md border border-success/25 bg-success/10 px-1.5 py-0.5 text-emerald-300">{b}</span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
