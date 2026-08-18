"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { supabaseEnabled } from "@/lib/supabase";
import { useAuth } from "./AuthProvider";
import { Logo } from "./Logo";
import { Badge, Button } from "./ui";

export function TopNav() {
  const router = useRouter();
  const { user, signOut } = useAuth();
  const [credits, setCredits] = useState<number | null>(null);

  async function refresh() {
    try {
      const me = await api.me();
      setCredits(me.credits);
    } catch {
      setCredits(null);
    }
  }

  useEffect(() => {
    refresh();
  }, [user]);

  async function topUp() {
    await api.refillCredits(25);
    refresh();
  }

  async function handleSignOut() {
    await signOut();
    router.replace("/login");
  }

  return (
    <header className="sticky top-0 z-20 border-b border-line bg-background/80 backdrop-blur">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-5">
        <div className="flex items-center gap-6">
          <Logo href="/dashboard" />
          <nav className="hidden gap-1 sm:flex">
            <Button href="/dashboard" variant="ghost" size="sm">Dashboard</Button>
          </nav>
        </div>
        <div className="flex items-center gap-3">
          {credits !== null && (
            <button onClick={topUp} title="Dev: refill credits" className="cursor-pointer">
              <Badge tone={credits > 0 ? "accent" : "danger"}>{credits} credits</Badge>
            </button>
          )}
          {supabaseEnabled && user && (
            <>
              <span className="hidden max-w-[12rem] truncate text-sm text-muted sm:block">{user.email}</span>
              <Button variant="ghost" size="sm" onClick={handleSignOut}>Sign out</Button>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
