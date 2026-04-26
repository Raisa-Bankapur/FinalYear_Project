import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Travel Buddy",
  description:
    "AI-powered trip planner with hotels, restaurants, and itinerary views.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
