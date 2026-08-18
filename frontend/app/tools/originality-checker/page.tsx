import type { Metadata } from "next";
import { ToolShell } from "@/components/tools/ToolShell";
import { OriginalityCheckerTool } from "@/components/tools/OriginalityCheckerTool";

export const metadata: Metadata = {
  title: "Free Originality / Reused-Content Checker",
  description:
    "Free tool: compare your script against a source and get a 0-100 originality score with flagged passages. Avoid YouTube's reused / inauthentic-content flags.",
  alternates: { canonical: "/tools/originality-checker" },
};

export default function Page() {
  return (
    <ToolShell
      title="Originality Checker"
      subtitle="Paste the original text and your version to get a 0-100 originality score, four similarity signals, and the exact passages that overlap. Free, instant, no signup."
    >
      <OriginalityCheckerTool />
    </ToolShell>
  );
}
