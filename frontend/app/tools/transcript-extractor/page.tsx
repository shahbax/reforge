import type { Metadata } from "next";
import { ToolShell } from "@/components/tools/ToolShell";
import { TranscriptExtractorTool } from "@/components/tools/TranscriptExtractorTool";

export const metadata: Metadata = {
  title: "Free YouTube Transcript Extractor",
  description:
    "Free tool: paste a YouTube URL and get the full video transcript, ready to copy. No signup required.",
  alternates: { canonical: "/tools/transcript-extractor" },
};

export default function Page() {
  return (
    <ToolShell
      title="Transcript Extractor"
      subtitle="Paste a YouTube URL to pull its full transcript, ready to copy. Free, no signup."
    >
      <TranscriptExtractorTool />
    </ToolShell>
  );
}
