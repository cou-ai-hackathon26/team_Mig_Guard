import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";

export const metadata: Metadata = {
  title: "Mig_Guard – Job Offer Checker for Migrant Workers",
  description:
    "Photograph a job offer or recruiter chat and get a Bangla verdict with red flags, missing clauses and questions to ask — before you leave.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    // lang is managed per-page via the <main lang="…"> attribute driven by the language toggle
    <html lang="en">
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
