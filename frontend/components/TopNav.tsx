"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Logo } from "./Logo";
import { Badge, Button } from "./ui";

export function TopNav() {
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
  }, []);

  async function topUp() {
    await api.refillCredits(25);
    refresh();
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
          <Button href="/dashboard" size="sm">New analysis</Button>
        </div>
      </div>
    </header>
  );
}
