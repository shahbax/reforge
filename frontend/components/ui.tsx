import Link from "next/link";
import type { ReactNode } from "react";
import type { Band, JobStatus } from "@/lib/types";

export function cn(...parts: (string | false | null | undefined)[]) {
  return parts.filter(Boolean).join(" ");
}

export function Button({
  children,
  onClick,
  href,
  variant = "primary",
  size = "md",
  disabled,
  type = "button",
  className,
}: {
  children: ReactNode;
  onClick?: () => void;
  href?: string;
  variant?: "primary" | "ghost" | "outline" | "danger";
  size?: "sm" | "md" | "lg";
  disabled?: boolean;
  type?: "button" | "submit";
  className?: string;
}) {
  const base =
    "inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus-visible:ring-2 focus-visible:ring-accent/60";
  const sizes = { sm: "px-3 py-1.5 text-sm", md: "px-4 py-2 text-sm", lg: "px-5 py-2.5 text-base" };
  const variants = {
    primary: "bg-accent text-white hover:bg-violet-500",
    ghost: "text-muted hover:text-foreground hover:bg-surface-solid",
    outline: "border border-line-strong text-foreground hover:bg-surface-solid",
    danger: "border border-danger/40 text-danger hover:bg-danger/10",
  };
  const cls = cn(base, sizes[size], variants[variant], className);
  if (href) return <Link href={href} className={cls}>{children}</Link>;
  return (
    <button type={type} onClick={onClick} disabled={disabled} className={cls}>
      {children}
    </button>
  );
}

export function Card({ children, className }: { children: ReactNode; className?: string }) {
  return <div className={cn("card p-5", className)}>{children}</div>;
}

export function Badge({
  children,
  tone = "neutral",
}: {
  children: ReactNode;
  tone?: "neutral" | "accent" | "success" | "warning" | "danger";
}) {
  const tones = {
    neutral: "bg-surface-solid text-muted border-line",
    accent: "bg-accent/15 text-violet-300 border-accent/30",
    success: "bg-success/15 text-emerald-300 border-success/30",
    warning: "bg-warning/15 text-amber-300 border-warning/30",
    danger: "bg-danger/15 text-red-300 border-danger/30",
  };
  return (
    <span className={cn("inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-medium", tones[tone])}>
      {children}
    </span>
  );
}

export function Spinner({ className }: { className?: string }) {
  return (
    <span
      className={cn("spin inline-block rounded-full border-2 border-line-strong border-t-accent", className ?? "h-4 w-4")}
      aria-hidden
    />
  );
}

export function Chips({ items, tone = "neutral" }: { items: string[]; tone?: "neutral" | "accent" }) {
  if (!items?.length) return null;
  return (
    <div className="flex flex-wrap gap-1.5">
      {items.map((it, i) => (
        <span
          key={i}
          className={cn(
            "rounded-md border px-2 py-1 text-xs",
            tone === "accent" ? "border-accent/25 bg-accent/10 text-violet-200" : "border-line bg-surface-solid text-muted",
          )}
        >
          {it}
        </span>
      ))}
    </div>
  );
}

export function Field({ label, hint, children }: { label: string; hint?: string; children: ReactNode }) {
  return (
    <label className="block space-y-1.5">
      <span className="text-sm font-medium text-foreground">{label}</span>
      {children}
      {hint && <span className="block text-xs text-muted-2">{hint}</span>}
    </label>
  );
}

const inputCls =
  "w-full rounded-lg border border-line bg-surface-solid px-3 py-2 text-sm text-foreground placeholder:text-muted-2 focus:border-accent/60 focus:outline-none focus:ring-2 focus:ring-accent/20";

export function TextInput(props: React.InputHTMLAttributes<HTMLInputElement>) {
  return <input {...props} className={cn(inputCls, props.className)} />;
}

export function Select(props: React.SelectHTMLAttributes<HTMLSelectElement>) {
  return <select {...props} className={cn(inputCls, "appearance-none", props.className)} />;
}

const STATUS_LABEL: Record<JobStatus, string> = {
  QUEUED: "Queued",
  DOWNLOADING: "Fetching video",
  TRANSCRIBING: "Transcribing",
  ANALYZING: "Analyzing",
  GENERATING_CONCEPTS: "Generating concepts",
  AWAITING_CONCEPT_SELECTION: "Ready",
  RESEARCHING: "Researching",
  GENERATING_SCRIPT: "Writing script",
  CHECKING_ORIGINALITY: "Checking originality",
  COMPLETED: "Completed",
  FAILED: "Failed",
};

export function StatusBadge({ status }: { status: JobStatus | null | undefined }) {
  if (!status) return <Badge>—</Badge>;
  const tone =
    status === "COMPLETED" || status === "AWAITING_CONCEPT_SELECTION"
      ? "success"
      : status === "FAILED"
        ? "danger"
        : "accent";
  return (
    <Badge tone={tone}>
      {tone === "accent" && <Spinner className="h-3 w-3" />}
      {STATUS_LABEL[status]}
    </Badge>
  );
}

export function bandTone(band: Band): "success" | "warning" | "danger" {
  return band === "LOW" ? "success" : band === "MODERATE" ? "warning" : "danger";
}
