import Link from "next/link";
import { Logo } from "@/components/Logo";
import { Badge, Button, Card } from "@/components/ui";
import { HeroPreview } from "@/components/landing/HeroPreview";
import { PipelineStack } from "@/components/landing/PipelineStack";

const PLANS = [
  { name: "Free", price: "$0", credits: "5 credits / month", featured: false, features: ["Full analyze → script pipeline", "Viral DNA + Originality Guard", "All free tools"] },
  { name: "Creator", price: "$19", credits: "60 credits / month", featured: true, features: ["Everything in Free", "All niches + tones", "Markdown / text exports", "Priority processing"] },
  { name: "Pro", price: "$39", credits: "200 credits / month", featured: false, features: ["Everything in Creator", "Deeper research mode", "Higher limits", "Channel analysis (soon)"] },
];

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000";

const description =
  "Reverse-engineer why a video went viral and create genuinely original scripts, with a built-in originality audit to help avoid YouTube's inauthentic-content penalties.";

const jsonLd = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "SoftwareApplication",
      name: "Reforge",
      applicationCategory: "BusinessApplication",
      operatingSystem: "Web",
      url: siteUrl,
      description,
      offers: [
        { "@type": "Offer", name: "Free", price: "0", priceCurrency: "USD" },
        { "@type": "Offer", name: "Creator", price: "19", priceCurrency: "USD" },
        { "@type": "Offer", name: "Pro", price: "39", priceCurrency: "USD" },
      ],
    },
    {
      "@type": "FAQPage",
      mainEntity: [
        { "@type": "Question", name: "Does Reforge copy the original video?", acceptedAnswer: { "@type": "Answer", text: "No. Reforge extracts the reusable mechanics (hook type, structure, pacing) and generates original concepts and scripts, then audits similarity against the source so your output isn't derivative." } },
        { "@type": "Question", name: "Will this help me avoid YouTube's inauthentic-content penalties?", acceptedAnswer: { "@type": "Answer", text: "Reforge is built to produce original, varied, human-editable scripts and gives every script an originality score. It is a tool to help you create original content, not a guarantee against policy actions." } },
        { "@type": "Question", name: "Do I need to be a video editor to use it?", acceptedAnswer: { "@type": "Answer", text: "No. Paste a YouTube URL, read the plain-language breakdown, pick a concept, and get a ready-to-film script plus titles and thumbnail prompts." } },
      ],
    },
  ],
};

const FEATURES = [
  { t: "Originality Guard", d: "A source-vs-generated similarity audit — phrase, distinctive-phrase, semantic and structural — with a 0–100 score and one-click rewrite. No competitor ships this.", badge: "Exclusive", span: true },
  { t: "Explainable Viral DNA", d: "Not a shallow hook/structure/CTA list — a structured mechanics report you can actually learn from." },
  { t: "Divergent by design", d: "Every concept states how it differs from the source. Mechanics are reusable; distinctive expression is not." },
  { t: "Research-grounded", d: "Fact / claim / opinion separation for factual niches, so your script doesn't hallucinate." },
];

export default function Landing() {
  return (
    <div className="bg-aurora min-h-screen overflow-x-hidden">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }} />

      {/* Nav */}
      <header className="mx-auto flex h-16 max-w-6xl items-center justify-between px-5">
        <Logo />
        <nav className="hidden items-center gap-6 md:flex">
          <Link href="#how" className="text-sm text-muted hover:text-foreground">How it works</Link>
          <Link href="#why" className="text-sm text-muted hover:text-foreground">Why Reforge</Link>
          <Link href="/tools" className="text-sm text-muted hover:text-foreground">Free tools</Link>
          <Link href="#pricing" className="text-sm text-muted hover:text-foreground">Pricing</Link>
        </nav>
        <div className="flex items-center gap-2">
          <Button href="/login" variant="ghost" size="sm">Log in</Button>
          <Button href="/login" size="sm">Start free</Button>
        </div>
      </header>

      {/* Hero */}
      <section className="mx-auto grid max-w-6xl items-center gap-10 px-5 pt-12 pb-16 lg:grid-cols-2 lg:pt-20">
        <div className="fade-up">
          <Badge tone="accent">Viral Content Intelligence + Original Generation</Badge>
          <h1 className="mt-5 text-balance text-5xl font-bold leading-[1.05] tracking-tight sm:text-6xl">
            See <span className="text-gradient">why</span> it went viral.
            <br />
            Make something <span className="text-gradient">original</span>.
          </h1>
          <p className="mt-6 max-w-xl text-pretty text-lg text-muted">
            Reforge reverse-engineers the mechanics behind any viral video and turns them into a
            genuinely original, ready-to-film script — with an originality score that keeps you off
            the wrong side of YouTube&apos;s inauthentic-content rules.
          </p>
          <div className="mt-8 flex flex-col gap-3 sm:flex-row">
            <Button href="/login" size="lg">Analyze a video free →</Button>
            <Button href="#how" variant="outline" size="lg">See how it works</Button>
          </div>
          <div className="mt-6 flex flex-wrap items-center gap-x-5 gap-y-2 text-xs text-muted-2">
            <span>✓ No credit card</span>
            <span>✓ 5 free credits/mo</span>
            <span>✓ Original by design, not a paraphraser</span>
          </div>
        </div>
        <div className="fade-up" style={{ animationDelay: "0.15s" }}>
          <HeroPreview />
        </div>
      </section>

      {/* Positioning band */}
      <section id="why" className="border-y border-line grid-bg">
        <div className="mx-auto max-w-4xl px-5 py-20 text-center">
          <div className="text-xs font-semibold uppercase tracking-[0.2em] text-accent">What Reforge actually is</div>
          <h2 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">
            Not a paraphraser. A viral-intelligence engine.
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-muted">
            Most tools either find viral videos or spit out template scripts. Reforge does the hard
            middle — it understands the mechanics, engineers divergent original angles, and audits the
            result so what you publish is yours.
          </p>
        </div>
      </section>

      {/* How it works — pipeline stack */}
      <section id="how" className="mx-auto max-w-6xl px-5 py-20">
        <div className="mx-auto mb-12 max-w-2xl text-center">
          <div className="text-xs font-semibold uppercase tracking-[0.2em] text-accent">How it works</div>
          <h2 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">From a viral video to your original script</h2>
          <p className="mt-4 text-muted">Five stages, one flow. Every step is explainable — no black box.</p>
        </div>
        <PipelineStack />
      </section>

      {/* Differentiators — bento */}
      <section className="mx-auto max-w-6xl px-5 pb-20">
        <div className="mb-10 max-w-2xl">
          <div className="text-xs font-semibold uppercase tracking-[0.2em] text-accent">Why we&apos;re different</div>
          <h2 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">Built on the gap competitors miss</h2>
        </div>
        <div className="grid gap-4 md:grid-cols-2">
          {FEATURES.map((f) => (
            <Card key={f.t} className={f.span ? "md:col-span-2 border-accent/25 bg-gradient-to-br from-accent/10 to-transparent" : ""}>
              <div className="flex items-center gap-2">
                <h3 className="text-lg font-semibold">{f.t}</h3>
                {f.badge && <Badge tone="accent">{f.badge}</Badge>}
              </div>
              <p className="mt-2 text-muted">{f.d}</p>
            </Card>
          ))}
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="mx-auto max-w-6xl px-5 pb-20">
        <div className="mx-auto mb-10 max-w-2xl text-center">
          <div className="text-xs font-semibold uppercase tracking-[0.2em] text-accent">Pricing</div>
          <h2 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">Start free. Upgrade when you&apos;re shipping.</h2>
          <p className="mt-4 text-muted">Annual plans save two months. Every plan includes the Originality Guard.</p>
        </div>
        <div className="grid gap-4 md:grid-cols-3">
          {PLANS.map((p) => (
            <Card key={p.name} className={p.featured ? "border-accent/40 ring-1 ring-accent/30" : ""}>
              {p.featured && <div className="mb-2"><Badge tone="accent">Most popular</Badge></div>}
              <h3 className="text-lg font-semibold">{p.name}</h3>
              <div className="mt-1 mb-1 text-3xl font-bold">
                {p.price}
                {p.price !== "$0" && <span className="text-base font-normal text-muted-2">/mo</span>}
              </div>
              <div className="mb-4 text-sm text-muted">{p.credits}</div>
              <ul className="mb-5 space-y-1.5 text-sm">
                {p.features.map((f) => (
                  <li key={f} className="flex gap-2 text-muted"><span className="text-success">✓</span>{f}</li>
                ))}
              </ul>
              <Button href="/login" variant={p.featured ? "primary" : "outline"} className="w-full">Start free</Button>
            </Card>
          ))}
        </div>
        <p className="mt-6 text-center text-xs text-muted-2">
          Need bulk or agency features? <span className="text-muted">Agency — $99/mo.</span>
        </p>
      </section>

      {/* Final CTA */}
      <section className="mx-auto max-w-6xl px-5 pb-24">
        <div className="relative overflow-hidden rounded-3xl border border-accent/30 bg-gradient-to-br from-accent/20 via-surface to-surface p-10 text-center sm:p-16">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">Reverse-engineer your next viral video</h2>
          <p className="mx-auto mt-3 max-w-lg text-muted">Paste a URL and get an original, audited script in minutes. Free to start.</p>
          <div className="mt-7 flex justify-center">
            <Button href="/login" size="lg">Get started free →</Button>
          </div>
          <p className="mt-6 text-xs text-muted-2">
            Originality analysis is an AI-based similarity assessment and is not legal advice or a guarantee against copyright claims.
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-line">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-5 py-8 sm:flex-row">
          <Logo />
          <nav className="flex flex-wrap items-center gap-5 text-sm text-muted-2">
            <Link href="#how" className="hover:text-foreground">How it works</Link>
            <Link href="/tools" className="hover:text-foreground">Free tools</Link>
            <Link href="#pricing" className="hover:text-foreground">Pricing</Link>
            <Link href="/login" className="hover:text-foreground">Log in</Link>
          </nav>
          <span className="text-sm text-muted-2">© {new Date().getFullYear()} Reforge</span>
        </div>
      </footer>
    </div>
  );
}
