import type { ReactNode } from "react";
import { Logo } from "@/components/Logo";
import { Button, Card } from "@/components/ui";

export function ToolShell({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle: string;
  children: ReactNode;
}) {
  return (
    <div className="bg-aurora min-h-screen">
      <header className="mx-auto flex h-16 max-w-4xl items-center justify-between px-5">
        <Logo />
        <div className="flex items-center gap-2">
          <Button href="/tools" variant="ghost" size="sm">Free tools</Button>
          <Button href="/dashboard" size="sm">Open app</Button>
        </div>
      </header>

      <main className="mx-auto max-w-3xl px-5 py-8">
        <h1 className="text-3xl font-bold tracking-tight">{title}</h1>
        <p className="mt-2 mb-8 text-muted">{subtitle}</p>

        {children}

        <Card className="mt-10 border-accent/25 bg-gradient-to-br from-accent/10 to-transparent text-center">
          <h3 className="text-lg font-semibold">Want the full pipeline?</h3>
          <p className="mx-auto mt-1 mb-4 max-w-lg text-sm text-muted">
            Reforge turns any viral video into original concepts and a ready-to-film script — with an
            originality score to help you avoid YouTube&apos;s inauthentic-content flags.
          </p>
          <Button href="/dashboard" size="lg">Try Reforge free →</Button>
        </Card>
      </main>

      <footer className="border-t border-line">
        <div className="mx-auto flex max-w-4xl items-center justify-between px-5 py-6 text-sm text-muted-2">
          <Logo />
          <span>© {new Date().getFullYear()} Reforge</span>
        </div>
      </footer>
    </div>
  );
}
