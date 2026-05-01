import "@/styles/globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "ProcurePilot - AI Procurement Copilot",
  description:
    "Intelligent procurement analysis and recommendations powered by AI",
  keywords: [
    "procurement",
    "AI",
    "analysis",
    "recommendations",
    "supply chain",
  ],
  authors: [{ name: "ProcurePilot Team" }],
  openGraph: {
    title: "ProcurePilot - AI Procurement Copilot",
    description:
      "Intelligent procurement analysis and recommendations powered by AI",
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
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold">P</span>
                </div>
                <h1 className="text-xl font-bold text-gray-900">ProcurePilot</h1>
              </div>
              <nav className="hidden sm:flex items-center gap-6">
                <a
                  href="/"
                  className="text-gray-600 hover:text-gray-900 font-medium text-sm"
                >
                  Home
                </a>
                <a
                  href="/dashboard"
                  className="text-gray-600 hover:text-gray-900 font-medium text-sm"
                >
                  Dashboard
                </a>
                <a
                  href="/requests"
                  className="btn-primary text-sm py-1.5 px-3"
                >
                  Requests
                </a>
              </nav>
            </div>
          </header>

          {/* Main content */}
          <main className="flex-1">{children}</main>

          {/* Footer */}
          <footer className="bg-gray-900 text-gray-100 border-t border-gray-800">
            <div className="container py-12">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-8 mb-8">
                <div>
                  <h3 className="font-semibold mb-4">ProcurePilot</h3>
                  <p className="text-gray-400 text-sm">
                    AI-powered procurement analysis for intelligent decision
                    making.
                  </p>
                </div>
                <div>
                  <h3 className="font-semibold mb-4">Product</h3>
                  <ul className="space-y-2 text-gray-400 text-sm">
                    <li>
                      <a href="/" className="hover:text-gray-200">
                        Features
                      </a>
                    </li>
                    <li>
                      <a href="/" className="hover:text-gray-200">
                        Pricing
                      </a>
                    </li>
                    <li>
                      <a href="/" className="hover:text-gray-200">
                        Documentation
                      </a>
                    </li>
                  </ul>
                </div>
                <div>
                  <h3 className="font-semibold mb-4">Legal</h3>
                  <ul className="space-y-2 text-gray-400 text-sm">
                    <li>
                      <a href="/" className="hover:text-gray-200">
                        Privacy
                      </a>
                    </li>
                    <li>
                      <a href="/" className="hover:text-gray-200">
                        Terms
                      </a>
                    </li>
                    <li>
                      <a href="/" className="hover:text-gray-200">
                        Security
                      </a>
                    </li>
                  </ul>
                </div>
              </div>

              <div className="border-t border-gray-800 pt-8 flex flex-col sm:flex-row items-center justify-between text-gray-400 text-sm">
                <p>&copy; 2025 ProcurePilot. All rights reserved.</p>
                <p>
                  Built with{" "}
                  <span className="text-danger-500">♥</span> for procurement
                  teams
                </p>
              </div>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
