"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api, ApiError } from "@/lib/api";
import type { ProjectSummary, Usage } from "@/lib/types";
import { TopNav } from "@/components/TopNav";
import { Badge, Button, Card, Spinner, StatusBadge, TextInput } from "@/components/ui";

export default function Dashboard() {
  const router = useRouter();
  const [url, setUrl] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [projects, setProjects] = useState<ProjectSummary[] | null>(null);
  const [usage, setUsage] = useState<Usage | null>(null);

  async function load() {
    const [p, u] = await Promise.allSettled([api.listProjects(), api.usage()]);
    if (p.status === "fulfilled") setProjects(p.value.projects);
    if (u.status === "fulfilled") setUsage(u.value);
  }

  useEffect(() => {
    load();
  }, []);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const { project_id } = await api.createAnalysis(url.trim());
      router.push(`/analysis/${project_id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong");
      setSubmitting(false);
    }
  }

  async function remove(id: string) {
    await api.deleteProject(id);
    load();
  }

  return (
    <>
      <TopNav />
      <main className="mx-auto max-w-6xl px-5 py-8">
        {/* New analysis */}
        <section className="mb-10">
          <h1 className="mb-1 text-2xl font-semibold tracking-tight">New analysis</h1>
          <p className="mb-4 text-sm text-muted">
            Paste a YouTube URL. Reforge extracts the Viral DNA and generates original concepts.
          </p>
          <Card>
            <form onSubmit={submit} className="flex flex-col gap-3 sm:flex-row">
              <TextInput
                type="url"
                required
                placeholder="https://www.youtube.com/watch?v=…"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                className="flex-1"
              />
              <Button type="submit" size="md" disabled={submitting || !url.trim()}>
                {submitting ? <><Spinner /> Starting…</> : "Analyze →"}
              </Button>
            </form>
            {error && <p className="mt-3 text-sm text-danger">{error}</p>}
            <p className="mt-3 text-xs text-muted-2">
              Dev mode uses a mock analysis engine — any valid YouTube URL works without API keys.
            </p>
          </Card>
        </section>

        <div className="grid gap-8 lg:grid-cols-3">
          {/* Recent projects */}
          <section className="lg:col-span-2">
            <h2 className="mb-3 text-lg font-semibold">Recent analyses</h2>
            {projects === null ? (
              <div className="space-y-2">
                {[0, 1, 2].map((i) => <div key={i} className="skeleton h-16 rounded-xl" />)}
              </div>
            ) : projects.length === 0 ? (
              <Card className="text-sm text-muted">No analyses yet. Paste a video above to begin.</Card>
            ) : (
              <div className="space-y-2">
                {projects.map((p) => (
                  <div
                    key={p.project_id}
                    className="group flex items-center justify-between gap-3 rounded-xl border border-line bg-surface p-4 transition-colors hover:border-line-strong"
                  >
                    <Link href={`/analysis/${p.project_id}`} className="min-w-0 flex-1">
                      <div className="truncate font-medium">{p.title || p.url}</div>
                      <div className="mt-1 flex items-center gap-2 text-xs text-muted-2">
                        <span className="uppercase">{p.platform}</span>
                        <span>·</span>
                        <span>{new Date(p.created_at).toLocaleString()}</span>
                        {p.originality_score !== null && (
                          <>
                            <span>·</span>
                            <span>Originality {p.originality_score}/100</span>
                          </>
                        )}
                      </div>
                    </Link>
                    <div className="flex items-center gap-2">
                      <StatusBadge status={p.script_status ?? p.status} />
                      <button
                        onClick={() => remove(p.project_id)}
                        className="text-muted-2 opacity-0 transition-opacity hover:text-danger group-hover:opacity-100"
                        title="Delete"
                      >
                        ✕
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>

          {/* Usage */}
          <section>
            <h2 className="mb-3 text-lg font-semibold">Usage</h2>
            <Card className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted">Credits remaining</span>
                <Badge tone={usage && usage.remaining_credits > 0 ? "accent" : "danger"}>
                  {usage?.remaining_credits ?? "—"}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted">Estimated spend</span>
                <span className="font-mono text-sm">${usage?.totals.cost_usd.toFixed(4) ?? "0.0000"}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted">Tokens</span>
                <span className="font-mono text-sm">
                  {((usage?.totals.input_tokens ?? 0) + (usage?.totals.output_tokens ?? 0)).toLocaleString()}
                </span>
              </div>
              <div className="border-t border-line pt-3">
                <Button variant="outline" size="sm" onClick={async () => { await api.refillCredits(25); load(); }}>
                  Refill dev credits
                </Button>
              </div>
            </Card>
          </section>
        </div>
      </main>
    </>
  );
}
