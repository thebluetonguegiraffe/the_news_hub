import type { Metadata } from "next";
import { Poppins } from "next/font/google";
import "./globals.css";
import { LanguageProvider } from "./contexts/LanguageContext";

const poppins = Poppins({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
  variable: "--font-poppins",
});

export const metadata: Metadata = {
  title: "The News Hub",
  description: "A modern dashboard for reading news articles and staying informed",
  icons: {
    icon: "/dashboard/app/favicon.ico",
    apple: "/apple-touch-icon.png",
    other: [
      {
        rel: "icon",
        type: "image/png",
        sizes: "192x192",
        url: "/android-chrome-192x192.png",
      },
    ],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${poppins.variable} antialiased`}>
        <LanguageProvider>
          {children}
        </LanguageProvider>
      </body>
    </html>
  );
}
