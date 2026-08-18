import Link from "next/link";
import { Logo } from "@/components/Logo";
import { Badge, Button, Card } from "@/components/ui";

const STEPS = [
  { n: "01", t: "Paste a viral video", d: "Drop a YouTube URL. Reforge fetches the transcript and mechanics — no re-watching." },
  { n: "02", t: "Extract the Viral DNA", d: "A deep, explainable breakdown: hook type, curiosity mechanism, emotional arc, open loops, retention hypotheses." },
  { n: "03", t: "Get original concepts", d: "5–10 genuinely different angles engineered to reuse the mechanics, not the wording." },
  { n: "04", t: "Write & audit the script", d: "A research-grounded script, then an Originality Guard that scores similarity and rewrites derivative passages." },
];

const FEATURES = [
  { t: "Originality Guard", d: "Source-vs-generated similarity audit — phrase, distinctive-phrase, semantic and structural — with a 0–100 score and one-click rewrite. Nobody else ships this.", tone: "accent" as const },
  { t: "Explainable Viral DNA", d: "Not a shallow hook/structure/CTA list — a structured mechanics report you can actually learn from.", tone: "neutral" as const },
  { t: "Divergent by design", d: "Every concept states how it differs from the source. Mechanics are reusable; distinctive expression is not.", tone: "neutral" as const },
  { t: "Research-grounded", d: "Fact / claim / opinion separation for factual niches, so your script doesn't hallucinate.", tone: "neutral" as const },
];

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000";

const jsonLd = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "SoftwareApplication",
      name: "Reforge",
      applicationCategory: "BusinessApplication",
      operatingSystem: "Web",
      url: siteUrl,
      description:
        "Reverse-engineer why a video went viral and create genuinely original scripts, with a built-in originality audit to help avoid YouTube's inauthentic-content penalties.",
      offers: [
        { "@type": "Offer", name: "Free", price: "0", priceCurrency: "USD" },
        { "@type": "Offer", name: "Creator", price: "19", priceCurrency: "USD" },
        { "@type": "Offer", name: "Pro", price: "39", priceCurrency: "USD" },
      ],
    },
    {
      "@type": "FAQPage",
      mainEntity: [
        {
          "@type": "Question",
          name: "Does Reforge copy the original video?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "No. Reforge extracts the reusable mechanics (hook type, structure, pacing) and generates original concepts and scripts, then audits similarity against the source so your output isn't derivative.",
          },
        },
        {
          "@type": "Question",
          name: "Will this help me avoid YouTube's inauthentic-content penalties?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "Reforge is built to produce original, varied, human-editable scripts and gives every script an originality score. It is a tool to help you create original content, not a guarantee against policy actions.",
          },
        },
        {
          "@type": "Question",
          name: "Do I need to be a video editor to use it?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "No. Paste a YouTube URL, read the plain-language breakdown, pick a concept, and get a ready-to-film script plus titles and thumbnail prompts.",
          },
        },
      ],
    },
  ],
};

export default function Landing() {
  return (
    <div className="bg-aurora min-h-screen">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }} />
      <header className="mx-auto flex h-16 max-w-6xl items-center justify-between px-5">
        <Logo />
        <div className="flex items-center gap-2">
          <Button href="/dashboard" variant="ghost" size="sm">Dashboard</Button>
          <Button href="/dashboard" size="sm">Open app</Button>
        </div>
      </header>

      <section className="mx-auto max-w-4xl px-5 pt-16 pb-20 text-center sm:pt-24">
        <div className="mb-5 flex justify-center">
          <Badge tone="accent">Viral Content Intelligence + Original Generation</Badge>
        </div>
        <h1 className="text-balance text-4xl font-bold leading-tight tracking-tight sm:text-6xl">
          Understand <span className="text-gradient">why</span> a video went viral.
          <br />
          Then make something <span className="text-gradient">original</span>.
        </h1>
        <p className="mx-auto mt-6 max-w-2xl text-pretty text-lg text-muted">
          Reforge reverse-engineers the mechanics behind a viral video and helps you create
          genuinely original content from those principles — with a built-in similarity audit
          that keeps you off the wrong side of derivative.
        </p>
        <div className="mt-9 flex flex-col items-center justify-center gap-3 sm:flex-row">
          <Button href="/dashboard" size="lg">Analyze a video →</Button>
          <Link href="#how" className="text-sm text-muted hover:text-foreground">See how it works</Link>
        </div>
        <p className="mt-4 text-xs text-muted-2">
          Not a copy-and-dodge-copyright tool. Reforge separates reusable mechanics from protectable expression.
        </p>
      </section>

      <section id="how" className="mx-auto max-w-6xl px-5 pb-16">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {STEPS.map((s) => (
            <Card key={s.n}>
              <div className="mb-3 font-mono text-sm text-accent">{s.n}</div>
              <h3 className="mb-1.5 font-semibold">{s.t}</h3>
              <p className="text-sm text-muted">{s.d}</p>
            </Card>
          ))}
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-5 pb-24">
        <h2 className="mb-2 text-2xl font-semibold tracking-tight">Built on the gap competitors miss</h2>
        <p className="mb-8 max-w-2xl text-muted">
          Most tools either find viral videos or spit out template scripts. Reforge does the hard
          middle — the mechanics, the divergence, and the originality check.
        </p>
        <div className="grid gap-4 sm:grid-cols-2">
          {FEATURES.map((f) => (
            <Card key={f.t} className="flex flex-col gap-2">
              <div className="flex items-center gap-2">
                <h3 className="font-semibold">{f.t}</h3>
                {f.tone === "accent" && <Badge tone="accent">Differentiator</Badge>}
              </div>
              <p className="text-sm text-muted">{f.d}</p>
            </Card>
          ))}
        </div>

        <div className="mt-10 rounded-2xl border border-line bg-surface p-6 text-center">
          <p className="text-sm text-muted">
            Originality analysis is an AI-based similarity assessment and is not legal advice or a
            guarantee against copyright claims.
          </p>
        </div>
      </section>

      <footer className="border-t border-line">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-5 py-6 text-sm text-muted-2">
          <Logo />
          <span>© {new Date().getFullYear()} Reforge · MVP</span>
        </div>
      </footer>
    </div>
  );
}
