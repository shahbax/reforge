// Typed client for the Reforge backend.
// In dev the backend runs in dev-auth mode (no login) and attributes requests to
// a single dev user, so no token is needed yet — Supabase auth is a later milestone.

import type {
  AnalysisView,
  Me,
  ProjectSummary,
  ScriptControls,
  ScriptView,
  Usage,
} from "./types";

export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000/api/v1";

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

async function req<T>(path: string, opts: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...opts,
    headers: {
      "Content-Type": "application/json",
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
  exportUrl: (id: string, format: "md" | "txt" = "md") =>
    `${API_BASE}/projects/${id}/export?format=${format}`,
};

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
