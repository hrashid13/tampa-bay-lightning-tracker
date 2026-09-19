import type { Metadata } from "next";
import { Saira_Condensed } from "next/font/google";
import "./globals.css";

// Condensed block face closest to the NHL "TAMPA BAY" wordmark lettering
const saira = Saira_Condensed({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: " Tampa Bay Lightning Stats",
  description: "Tampa Bay Lightning organization player statistics dashboard",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={saira.className}>
        {children}
      </body>
    </html>
  );
}