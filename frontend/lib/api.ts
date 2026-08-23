// Typed client for the ViralReverse backend.
// In dev the backend runs in dev-auth mode (no login) and attributes requests to
// a single dev user, so no token is needed yet — Supabase auth is a later milestone.

import { supabase } from "./supabase";
import type {
  AnalysisView,
  HookResult,
  Me,
  OriginalityReport,
  ProjectSummary,
  ScriptControls,
  ScriptView,
  TranscriptResult,
  Usage,
} from "./types";

export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000/api/v1";

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

/** Attach the current Supabase access token (if signed in). In dev-auth mode
 *  there's no token and the backend attributes requests to a dev user. */
async function authHeaders(): Promise<Record<string, string>> {
  if (!supabase) return {};
  const { data } = await supabase.auth.getSession();
  const token = data.session?.access_token;
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function req<T>(path: string, opts: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...opts,
    headers: {
      "Content-Type": "application/json",
      ...(await authHeaders()),
      ...(opts.headers ?? {}),
    },
    cache: "no-store",
  });
  if (res.status === 204) return undefined as T;
  const text = await res.text();
  const body = text ? JSON.parse(text) : null;
  if (!res.ok) {
    const message = body?.error?.message ?? body?.detail ?? res.statusText;
    throw new ApiError(res.status, String(message));
  }
  return body as T;
}

/** Fetch a text document (export) with auth and trigger a browser download. */
async function downloadText(path: string, filename: string): Promise<void> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: await authHeaders(),
    cache: "no-store",
  });
  if (!res.ok) throw new ApiError(res.status, res.statusText);
  const text = await res.text();
  const url = URL.createObjectURL(new Blob([text], { type: "text/plain" }));
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export const api = {
  me: () => req<Me>("/me"),
  refillCredits: (credits = 25) =>
    req<{ credits: number }>(`/me/credits/refill?credits=${credits}`, { method: "POST" }),
  usage: () => req<Usage>("/usage"),

  createAnalysis: (url: string) =>
    req<{ project_id: string; status: string; deduped?: boolean }>("/analyses", {
      method: "POST",
      body: JSON.stringify({ url }),
    }),
  getAnalysis: (id: string) => req<AnalysisView>(`/analyses/${id}`),

  listProjects: () => req<{ projects: ProjectSummary[]; next_cursor: string | null }>("/projects"),
  deleteProject: (id: string) => req<void>(`/projects/${id}`, { method: "DELETE" }),

  startScript: (id: string, conceptIndex: number, controls: Partial<ScriptControls>) =>
    req<{ script_job: string; script_id: string; status: string }>(
      `/projects/${id}/script`,
      { method: "POST", body: JSON.stringify({ concept_index: conceptIndex, controls }) },
    ),
  getScript: (id: string) => req<ScriptView>(`/projects/${id}/script`),
  rewrite: (scriptId: string, target: "flagged" | "all" = "flagged") =>
    req<{ status: string; script_id: string }>(`/scripts/${scriptId}/rewrite`, {
      method: "POST",
      body: JSON.stringify({ target }),
    }),
  exportScript: (id: string, format: "md" | "txt" = "md") =>
    downloadText(`/projects/${id}/export?format=${format}`, `viralreverse-script-${id.slice(0, 8)}.${format}`),

  // Public tools (no auth required)
  originalityTool: (source: string, generated: string) =>
    req<OriginalityReport>("/tools/originality", { method: "POST", body: JSON.stringify({ source, generated }) }),
  hookTool: (text: string) =>
    req<HookResult>("/tools/hook", { method: "POST", body: JSON.stringify({ text }) }),
  transcriptTool: (url: string) =>
    req<TranscriptResult>("/tools/transcript", { method: "POST", body: JSON.stringify({ url }) }),

  // Billing
  createCheckout: (plan: string) =>
    req<{ url: string }>("/billing/checkout", { method: "POST", body: JSON.stringify({ plan }) }),
};

/** Start Stripe Checkout for a plan and redirect the browser to it. */
export async function startCheckout(plan: string): Promise<void> {
  const { url } = await api.createCheckout(plan);
  window.location.href = url;
}

/** Poll a fetcher until `done` returns true (or attempts run out). */
export async function poll<T>(
  fetcher: () => Promise<T>,
  done: (v: T) => boolean,
  { intervalMs = 900, maxAttempts = 120 }: { intervalMs?: number; maxAttempts?: number } = {},
): Promise<T> {
  let last = await fetcher();
  let n = 0;
  while (!done(last) && n < maxAttempts) {
    await new Promise((r) => setTimeout(r, intervalMs));
    last = await fetcher();
    n += 1;
  }
  return last;
}
