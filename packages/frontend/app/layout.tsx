import type React from "react"
import type { Metadata } from "next"
import { GeistSans } from "geist/font/sans"
import { GeistMono } from "geist/font/mono"
// import { Analytics } from "@vercel/analytics/next"
import "./globals.css"
import { Providers } from "@/app/providers"
import { Suspense } from "react"

export const metadata: Metadata = {
  title: "AndrehSatoru",
  description: "Criado por Andreh Satoru",
  generator: "AndrehSatoru",
  icons: {
    icon: "/favicon.svg",
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="pt-BR" className="antialiased">
      <body className={`font-sans ${GeistSans.variable} ${GeistMono.variable}`}>
        <Suspense fallback={null}>
          <Providers>{children}</Providers>
        </Suspense>
      </body>
    </html>
  )
}
