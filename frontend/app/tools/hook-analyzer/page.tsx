import type { Metadata } from "next";
import { ToolShell } from "@/components/tools/ToolShell";
import { HookAnalyzerTool } from "@/components/tools/HookAnalyzerTool";

export const metadata: Metadata = {
  title: "Free YouTube Hook Analyzer",
  description:
    "Free tool: score your video's opening hook and get instant, specific suggestions to make it grab attention in the first 5 seconds.",
  alternates: { canonical: "/tools/hook-analyzer" },
};

export default function Page() {
  return (
    <ToolShell
      title="Hook Analyzer"
      subtitle="Paste your opening line to get a strength score, a breakdown of what's working, and specific fixes. Free, instant, no signup."
    >
      <HookAnalyzerTool />
    </ToolShell>
  );
}
