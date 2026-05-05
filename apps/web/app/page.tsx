"use client";

import { api } from "@/services/api";
import Link from "next/link";
import { useEffect, useState } from "react";

export default function HomePage() {
  const [isAvailable, setIsAvailable] = useState<boolean | null>(null);

  useEffect(() => {
    api.isAvailable().then(setIsAvailable);
  }, []);

  return (
    <div className="space-y-20">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-primary-50 to-primary-100 py-20 px-4">
        <div className="container max-w-4xl">
          <div className="text-center space-y-6">
            <div className="inline-flex items-center gap-2">
              <span className="badge badge-primary text-sm">
                🇮🇳 Built for Indian Procurement
              </span>
            </div>

            <h1 className="text-4xl sm:text-5xl font-bold text-gray-900">
              AI-Powered Indian
              <br />
              Procurement Copilot
            </h1>

            <p className="text-xl text-gray-700 max-w-2xl mx-auto">
              Analyse procurement requests in seconds. Get GFR 2017-aligned policy
              checks, GST-aware risk assessment, MSME preference flags, and
              actionable recommendations — powered by AI.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center pt-4">
              <Link href="/dashboard" className="btn-primary btn-large">
                Start Analysis
              </Link>
              <Link href="/requests" className="btn-secondary btn-large">
                View Requests
              </Link>
            </div>

            {/* API Status */}
            <div className="mt-8 pt-8 border-t border-primary-200">
              {isAvailable === null && (
                <p className="text-sm text-gray-500">Checking service status...</p>
              )}
              {isAvailable === true && (
                <div className="alert alert-success inline-block text-sm">
                  ✓ Backend API is online and ready
                </div>
              )}
              {isAvailable === false && (
                <div className="alert alert-warning inline-block text-sm">
                  ⚠ Backend API is unavailable. Start the FastAPI server to analyse requests.
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="section">
        <div className="container">
          <h2 className="text-3xl font-bold text-center mb-12">
            What ProcurePilot Does
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: "📝",
                title: "Request Normalisation",
                desc: "Submit in plain language. AI structures and standardises your procurement request automatically.",
              },
              {
                icon: "📋",
                title: "Requirement Extraction",
                desc: "Extracts MUST_HAVE, SHOULD_HAVE, and NICE_TO_HAVE requirements from your description.",
              },
              {
                icon: "⚖️",
                title: "GFR Policy Retrieval",
                desc: "Retrieves relevant GFR 2017, GeM, CPWD, and MeitY policies for your procurement category.",
              },
              {
                icon: "⚠️",
                title: "Risk Assessment",
                desc: "Identifies compliance gaps, approval threshold breaches, and vendor-related risks.",
              },
              {
                icon: "💡",
                title: "Smart Recommendations",
                desc: "Prioritised P1/P2/P3 action items with responsible parties and timelines.",
              },
              {
                icon: "📊",
                title: "Confidence Scoring",
                desc: "Every analysis comes with a confidence score so you know how reliable the recommendation is.",
              },
            ].map((f) => (
              <div key={f.title} className="card">
                <div className="card-body space-y-3">
                  <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                    <span className="text-2xl" aria-hidden="true">{f.icon}</span>
                  </div>
                  <h3 className="font-semibold text-lg">{f.title}</h3>
                  <p className="text-gray-600 text-sm">{f.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Indian Compliance Section */}
      <section className="bg-gray-50 section">
        <div className="container max-w-4xl">
          <h2 className="text-3xl font-bold text-center mb-4">
            Built for Indian Procurement Rules
          </h2>
          <p className="text-center text-gray-600 mb-12">
            Every analysis is aware of the Indian regulatory and compliance landscape.
          </p>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-6">
            {[
              { label: "GFR 2017", desc: "General Financial Rules" },
              { label: "GeM Portal", desc: "e-Marketplace alignment" },
              { label: "MSME/Udyam", desc: "Price preference support" },
              { label: "GST Ready", desc: "Vendor compliance checks" },
            ].map((item) => (
              <div
                key={item.label}
                className="card text-center"
              >
                <div className="card-body py-6">
                  <p className="font-bold text-primary-700 text-lg">{item.label}</p>
                  <p className="text-xs text-gray-500 mt-1">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="section">
        <div className="container max-w-3xl">
          <h2 className="text-3xl font-bold text-center mb-12">How It Works</h2>

          <div className="space-y-8">
            {[
              {
                step: 1,
                title: "Submit Your Procurement Request",
                desc: "Fill in the request form with title, description, category (IT Hardware, Works, Services, etc.), budget in INR, and urgency level.",
              },
              {
                step: 2,
                title: "AI Runs 5-Stage Analysis",
                desc: "The AI pipeline runs: request normalisation → requirement extraction → GFR policy retrieval → risk evaluation → recommendation generation.",
              },
              {
                step: 3,
                title: "Review Structured Results",
                desc: "Get extracted requirements, applicable GFR/GeM policies, risk flags with severities, and prioritised action items.",
              },
              {
                step: 4,
                title: "Take Action with Confidence",
                desc: "Use the confidence score and recommendations to route for approval, shortlist vendors, or raise an RFQ.",
              },
            ].map((s) => (
              <div key={s.step} className="flex gap-6">
                <div className="flex-shrink-0">
                  <div className="w-10 h-10 rounded-full bg-primary-600 text-white flex items-center justify-center font-bold">
                    {s.step}
                  </div>
                </div>
                <div>
                  <h3 className="font-semibold text-lg mb-1">{s.title}</h3>
                  <p className="text-gray-600">{s.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="section bg-primary-600 text-white">
        <div className="container max-w-2xl text-center space-y-6">
          <h2 className="text-3xl font-bold">
            Ready to Streamline Your Procurement?
          </h2>
          <p className="text-lg opacity-90">
            Get GFR-compliant procurement analysis in seconds — not days.
          </p>
          <Link
            href="/dashboard"
            className="btn-primary bg-white text-primary-600 hover:bg-gray-100 btn-large inline-block"
          >
            Start Analysing Now
          </Link>
        </div>
      </section>
    </div>
  );
}
