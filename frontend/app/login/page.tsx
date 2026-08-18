"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Logo } from "@/components/Logo";
import { Button, Card, Field, Spinner, TextInput } from "@/components/ui";
import { useAuth } from "@/components/AuthProvider";
import { supabase, supabaseEnabled } from "@/lib/supabase";

type Mode = "signin" | "signup";

export default function LoginPage() {
  const router = useRouter();
  const { user, loading } = useAuth();
  const [mode, setMode] = useState<Mode>("signin");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  // Already signed in → go to the app.
  useEffect(() => {
    if (!loading && user) router.replace("/dashboard");
  }, [loading, user, router]);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!supabase) return;
    setBusy(true);
    setError(null);
    setNotice(null);
    try {
      if (mode === "signup") {
        const { data, error } = await supabase.auth.signUp({ email, password });
        if (error) throw error;
        if (!data.session) {
          setNotice("Account created. Check your email to confirm, then sign in.");
          setMode("signin");
          return;
        }
        router.replace("/dashboard");
      } else {
        const { error } = await supabase.auth.signInWithPassword({ email, password });
        if (error) throw error;
        router.replace("/dashboard");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Authentication failed");
    } finally {
      setBusy(false);
    }
  }

  async function google() {
    if (!supabase) return;
    setError(null);
    const { error } = await supabase.auth.signInWithOAuth({
      provider: "google",
      options: { redirectTo: `${window.location.origin}/dashboard` },
    });
    if (error) setError(error.message);
  }

  return (
    <div className="bg-aurora grid min-h-screen place-items-center px-5">
      <div className="w-full max-w-sm">
        <div className="mb-6 flex justify-center">
          <Logo href="/" />
        </div>
        <Card className="space-y-5">
          <div className="text-center">
            <h1 className="text-xl font-semibold">
              {mode === "signin" ? "Welcome back" : "Create your account"}
            </h1>
            <p className="mt-1 text-sm text-muted">
              {mode === "signin" ? "Sign in to your Reforge workspace." : "Start reverse-engineering virality."}
            </p>
          </div>

          {!supabaseEnabled ? (
            <p className="rounded-lg border border-warning/30 bg-warning/5 p-3 text-sm text-amber-200">
              Auth isn’t configured. Set the Supabase env vars, or continue in dev mode.
            </p>
          ) : (
            <form onSubmit={submit} className="space-y-3">
              <Field label="Email">
                <TextInput type="email" required autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" />
              </Field>
              <Field label="Password">
                <TextInput type="password" required autoComplete={mode === "signin" ? "current-password" : "new-password"} minLength={6} value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" />
              </Field>
              {error && <p className="text-sm text-danger">{error}</p>}
              {notice && <p className="text-sm text-emerald-300">{notice}</p>}
              <Button type="submit" size="lg" disabled={busy} className="w-full">
                {busy ? <><Spinner /> Please wait…</> : mode === "signin" ? "Sign in" : "Sign up"}
              </Button>
            </form>
          )}

          {supabaseEnabled && (
            <>
              <div className="flex items-center gap-3 text-xs text-muted-2">
                <span className="h-px flex-1 bg-line" /> or <span className="h-px flex-1 bg-line" />
              </div>
              <Button variant="outline" size="md" className="w-full" onClick={google}>
                Continue with Google
              </Button>
            </>
          )}

          <p className="text-center text-sm text-muted">
            {mode === "signin" ? "New here? " : "Already have an account? "}
            <button
              className="text-accent hover:underline"
              onClick={() => { setMode(mode === "signin" ? "signup" : "signin"); setError(null); setNotice(null); }}
            >
              {mode === "signin" ? "Create an account" : "Sign in"}
            </button>
          </p>
        </Card>
      </div>
    </div>
  );
}
