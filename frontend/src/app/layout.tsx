import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/Navbar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "LuminaShield | AI Plagiarism Detector",
  description: "Detección avanzada de firmas de IA y plagio en código.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es">
      <body className={`${inter.className} bg-background text-foreground antialiased`}>
        <Navbar />
        <main className="pt-24 min-h-screen px-8">
          {children}
        </main>
      </body>
    </html>
  );
}
