import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/components/AuthProvider";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000";

const description =
  "ViralReverse reverse-engineers why a video went viral and helps you create genuinely original scripts — with a built-in originality audit that helps you avoid YouTube's inauthentic-content penalties.";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: "ViralReverse — Reverse-Engineer Viral Videos into Original Scripts",
    template: "%s · ViralReverse",
  },
  description,
  applicationName: "ViralReverse",
  keywords: [
    "youtube script generator",
    "faceless youtube automation",
    "viral video analyzer",
    "ai script writer",
    "youtube content ideas",
    "video to script",
    "original content generator",
    "youtube automation tools",
    "avoid inauthentic content youtube",
  ],
  alternates: { canonical: siteUrl },
  robots: { index: true, follow: true },
  openGraph: {
    type: "website",
    url: siteUrl,
    siteName: "ViralReverse",
    title: "ViralReverse — Reverse-Engineer Viral Videos into Original Scripts",
    description,
  },
  twitter: {
    card: "summary_large_image",
    title: "ViralReverse — Reverse-Engineer Viral Videos into Original Scripts",
    description,
  },
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
