import type { Metadata } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: "Stock Trend Scanner",
  description: "Portfolio-ready stock scanner dashboard built with Next.js and FastAPI.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className="dark">
      <body>{children}</body>
    </html>
  );
}
