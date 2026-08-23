"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api, ApiError, startCheckout } from "@/lib/api";
import type { ProjectSummary, Usage } from "@/lib/types";
import { TopNav } from "@/components/TopNav";
import { useRequireAuth } from "@/components/AuthProvider";
import { supabaseEnabled } from "@/lib/supabase";
import { Badge, Button, Card, Spinner, StatusBadge, TextInput } from "@/components/ui";

const EXAMPLE_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ";

function FullPageLoader() {
  return (
    <div className="grid min-h-screen place-items-center bg-background">
      <Spinner className="h-6 w-6" />
    </div>
  );
}

export default function Dashboard() {
  const router = useRouter();
  const { user: authUser, loading: authLoading } = useRequireAuth();
  const [url, setUrl] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [projects, setProjects] = useState<ProjectSummary[] | null>(null);
  const [usage, setUsage] = useState<Usage | null>(null);
  const [checkoutMsg, setCheckoutMsg] = useState<string | null>(null);

  useEffect(() => {
    const p = new URLSearchParams(window.location.search).get("checkout");
    if (p === "success") setCheckoutMsg("🎉 Payment received — your credits will update within a few seconds.");
    else if (p === "cancel") setCheckoutMsg("Checkout canceled — no charge was made.");
  }, []);

  async function load() {
    const [p, u] = await Promise.allSettled([api.listProjects(), api.usage()]);
    if (p.status === "fulfilled") setProjects(p.value.projects);
    if (u.status === "fulfilled") setUsage(u.value);
  }

  useEffect(() => {
    if (authLoading) return;
    if (supabaseEnabled && !authUser) return;
    load();
  }, [authLoading, authUser]);

  async function startAnalysis(targetUrl: string) {
    setError(null);
    setSubmitting(true);
    try {
      const { project_id } = await api.createAnalysis(targetUrl.trim());
      router.push(`/analysis/${project_id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong");
      setSubmitting(false);
    }
  }

  function submit(e: React.FormEvent) {
    e.preventDefault();
    startAnalysis(url);
  }

  async function remove(id: string) {
    await api.deleteProject(id);
    load();
  }

  if (authLoading) return <FullPageLoader />;
  if (supabaseEnabled && !authUser) return null;

  return (
    <>
      <TopNav />
      <main className="mx-auto max-w-6xl px-5 py-8">
        {checkoutMsg && (
          <div className="mb-6 rounded-xl border border-accent/30 bg-accent/10 px-4 py-3 text-sm text-violet-100">
            {checkoutMsg}
          </div>
        )}

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
            <div className="mt-3 flex flex-wrap items-center gap-2">
              <button
                onClick={() => startAnalysis(EXAMPLE_URL)}
                disabled={submitting}
                className="text-xs text-accent hover:underline disabled:opacity-50"
              >
                ✨ Try an example (no URL needed)
              </button>
              <span className="text-xs text-muted-2">— not sure what to paste? Start here.</span>
            </div>
          </Card>
        </section>

        {projects !== null && projects.length === 0 && (
          <section className="mb-10">
            <div className="rounded-2xl border border-line bg-surface p-5">
              <h2 className="mb-3 text-sm font-semibold text-muted">How Reforge works</h2>
              <div className="grid gap-4 sm:grid-cols-3">
                {[
                  { n: "1", t: "Paste a video you admire", d: "Any YouTube video that's clearly working in your niche." },
                  { n: "2", t: "See why it worked", d: "A plain-language breakdown of its hook, structure, and pacing — no jargon left unexplained." },
                  { n: "3", t: "Get an original script", d: "Pick a fresh angle and get a ready-to-film script, checked for originality." },
                ].map((s) => (
                  <div key={s.n} className="flex gap-3">
                    <span className="grid h-6 w-6 shrink-0 place-items-center rounded-full bg-accent/15 text-xs font-semibold text-violet-300">{s.n}</span>
                    <div>
                      <div className="text-sm font-medium">{s.t}</div>
                      <div className="text-sm text-muted">{s.d}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </section>
        )}

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
                <Button variant="ghost" size="sm" onClick={async () => { await api.refillCredits(25); load(); }}>
                  Refill dev credits
                </Button>
              </div>
            </Card>

            <Card className="mt-4 space-y-2.5">
              <div>
                <h3 className="font-semibold">Upgrade</h3>
                <p className="text-xs text-muted-2">More credits, billed monthly. Cancel anytime.</p>
              </div>
              {[
                { plan: "creator", label: "Creator", price: "$19", credits: "60 credits/mo" },
                { plan: "pro", label: "Pro", price: "$39", credits: "200 credits/mo" },
                { plan: "agency", label: "Agency", price: "$99", credits: "400 credits/mo" },
              ].map((p) => (
                <button
                  key={p.plan}
                  onClick={() => startCheckout(p.plan)}
                  className="flex w-full items-center justify-between rounded-lg border border-line bg-surface-solid px-3 py-2 text-left transition-colors hover:border-accent/50"
                >
                  <span className="text-sm">
                    <span className="font-medium">{p.label}</span>
                    <span className="text-muted-2"> · {p.credits}</span>
                  </span>
                  <span className="text-sm font-semibold text-accent">{p.price}</span>
                </button>
              ))}
              <p className="text-[10px] text-muted-2">Secure checkout via Stripe.</p>
            </Card>
          </section>
        </div>
      </main>
    </>
  );
}
