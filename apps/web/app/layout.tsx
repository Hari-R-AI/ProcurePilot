import "@/styles/globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "ProcurePilot — Indian AI Procurement Copilot",
  description:
    "AI-powered Indian procurement analysis: GFR compliance, GST-ready vendor checks, risk assessment, and actionable recommendations.",
  keywords: [
    "procurement",
    "AI",
    "India",
    "GFR",
    "GeM",
    "GST",
    "procurement analysis",
    "supply chain",
    "MSME",
  ],
  authors: [{ name: "ProcurePilot Team" }],
  openGraph: {
    title: "ProcurePilot — Indian AI Procurement Copilot",
    description:
      "AI-powered procurement analysis with GFR compliance, risk assessment, and actionable recommendations for Indian procurement teams.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen bg-gray-50 flex flex-col">
          {/* Header */}
          <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
            <div className="container py-4 flex items-center justify-between">
              {/* Logo */}
              <a href="/" className="flex items-center gap-2 no-underline">
                <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center flex-shrink-0">
                  <span className="text-white font-bold text-sm">P</span>
                </div>
                <span className="text-xl font-bold text-gray-900">
                  ProcurePilot
                </span>
                <span className="hidden sm:inline text-xs text-gray-400 font-normal ml-1">
                  India
                </span>
              </a>

              {/* Desktop nav */}
              <nav className="hidden sm:flex items-center gap-6" aria-label="Main navigation">
                <a
                  href="/"
                  className="text-gray-600 hover:text-gray-900 font-medium text-sm no-underline"
                >
                  Home
                </a>
                <a
                  href="/dashboard"
                  className="text-gray-600 hover:text-gray-900 font-medium text-sm no-underline"
                >
                  Dashboard
                </a>
                <a
                  href="/requests"
                  className="text-gray-600 hover:text-gray-900 font-medium text-sm no-underline"
                >
                  My Requests
                </a>
                <a
                  href="/dashboard"
                  className="btn-primary text-sm py-1.5 px-4 no-underline"
                >
                  New Analysis
                </a>
              </nav>

              {/* Mobile nav — minimal */}
              <div className="sm:hidden flex items-center gap-3">
                <a
                  href="/dashboard"
                  className="btn-primary text-sm py-1.5 px-3 no-underline"
                >
                  Analyse
                </a>
                <a
                  href="/requests"
                  className="text-gray-600 hover:text-gray-900 text-sm font-medium no-underline"
                >
                  History
                </a>
              </div>
            </div>
          </header>

          {/* Main content */}
          <main className="flex-1">{children}</main>

          {/* Footer */}
          <footer className="bg-gray-900 text-gray-100 border-t border-gray-800">
            <div className="container py-12">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-8 mb-8">
                <div>
                  <h3 className="font-semibold mb-3">ProcurePilot India</h3>
                  <p className="text-gray-400 text-sm">
                    AI-powered procurement analysis for Indian government and
                    enterprise teams. GFR 2017 compliant, GeM-aware, MSME-ready.
                  </p>
                </div>
                <div>
                  <h3 className="font-semibold mb-3">Platform</h3>
                  <ul className="space-y-2 text-gray-400 text-sm">
                    <li>
                      <a href="/dashboard" className="hover:text-gray-200 no-underline">
                        Procurement Analysis
                      </a>
                    </li>
                    <li>
                      <a href="/requests" className="hover:text-gray-200 no-underline">
                        Request History
                      </a>
                    </li>
                    <li>
                      <a href="/" className="hover:text-gray-200 no-underline">
                        How It Works
                      </a>
                    </li>
                  </ul>
                </div>
                <div>
                  <h3 className="font-semibold mb-3">Compliance</h3>
                  <ul className="space-y-2 text-gray-400 text-sm">
                    <li>
                      <span className="text-gray-500">GFR 2017</span>
                    </li>
                    <li>
                      <span className="text-gray-500">GeM Portal Aligned</span>
                    </li>
                    <li>
                      <span className="text-gray-500">MSME / Udyam Ready</span>
                    </li>
                    <li>
                      <span className="text-gray-500">GST Compliance</span>
                    </li>
                  </ul>
                </div>
              </div>

              <div className="border-t border-gray-800 pt-8 flex flex-col sm:flex-row items-center justify-between text-gray-400 text-sm gap-4">
                <p>&copy; {new Date().getFullYear()} ProcurePilot. All rights reserved.</p>
                <p>
                  Built for India&apos;s procurement teams
                </p>
              </div>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
