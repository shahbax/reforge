import type { Metadata } from "next";
import Link from "next/link";
import { ToolShell } from "@/components/tools/ToolShell";
import { Card } from "@/components/ui";

export const metadata: Metadata = {
  title: "Free YouTube Creator Tools",
  description:
    "Free, no-signup tools for YouTube creators: an originality / reused-content checker, a hook analyzer, and a transcript extractor.",
  alternates: { canonical: "/tools" },
};

const TOOLS = [
  { href: "/tools/originality-checker", t: "Originality Checker", d: "Compare two texts and get a reused-content similarity score — helps you avoid YouTube's inauthentic-content flags." },
  { href: "/tools/hook-analyzer", t: "Hook Analyzer", d: "Score your video's opening line and get specific suggestions to make it grab attention." },
  { href: "/tools/transcript-extractor", t: "Transcript Extractor", d: "Paste a YouTube URL and get the full transcript, ready to copy." },
];

export default function ToolsIndex() {
  return (
    <ToolShell title="Free creator tools" subtitle="Handy, no-signup tools for YouTube creators — powered by the same engine behind Reforge.">
      <div className="grid gap-3">
        {TOOLS.map((x) => (
          <Link key={x.href} href={x.href}>
            <Card className="transition-colors hover:border-line-strong">
              <h3 className="font-semibold">{x.t}</h3>
              <p className="mt-1 text-sm text-muted">{x.d}</p>
            </Card>
          </Link>
        ))}
      </div>
    </ToolShell>
  );
}
