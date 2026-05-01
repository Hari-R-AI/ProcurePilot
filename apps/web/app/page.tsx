"use client";

import { api } from "@/services/api";
import Link from "next/link";
import { useEffect, useState } from "react";

export default function HomePage() {
  const [isAvailable, setIsAvailable] = useState<boolean | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const checkAPI = async () => {
      try {
        const available = await api.isAvailable();
        setIsAvailable(available);
      } catch (err) {
        setIsAvailable(false);
        setError("Backend API is not available");
      }
    };

    checkAPI();
  }, []);

  return (
    <div className="space-y-20">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-primary-50 to-primary-100 py-20 px-4">
        <div className="container max-w-4xl">
          <div className="text-center space-y-6">
            <div className="inline-block">
              <span className="badge badge-primary text-sm">
                ✨ Powered by AI
              </span>
            </div>

            <h1 className="text-4xl sm:text-5xl font-bold text-gray-900">
              Intelligent Procurement Analysis
            </h1>

            <p className="text-xl text-gray-700 max-w-2xl mx-auto">
              Get AI-powered procurement recommendations. Analyze requests,
              extract requirements, evaluate risks, and receive actionable
              recommendations in seconds.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center pt-4">
              <Link href="/dashboard" className="btn-primary btn-large">
                Start Analysis
              </Link>
              <button className="btn-secondary btn-large">Learn More</button>
            </div>

            {/* API Status */}
            <div className="mt-8 pt-8 border-t border-primary-200">
              {isAvailable === null && (
                <p className="text-sm text-gray-600">Checking API status...</p>
              )}
              {isAvailable === true && (
                <div className="alert alert-success inline-block">
                  ✓ Backend API is available
                </div>
              )}
              {isAvailable === false && (
                <div className="alert alert-warning inline-block">
                  ⚠ Backend API is not available. Using demo mode.
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="section">
        <div className="container">
          <h2 className="text-3xl font-bold text-center mb-12">Key Features</h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="card">
              <div className="card-body space-y-4">
                <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                  <span className="text-2xl">📝</span>
                </div>
                <h3 className="font-semibold text-lg">Request Analysis</h3>
                <p className="text-gray-600">
                  Submit procurement requests in natural language. AI normalizes
                  and structures your requests.
                </p>
              </div>
            </div>

            {/* Feature 2 */}
            <div className="card">
              <div className="card-body space-y-4">
                <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                  <span className="text-2xl">📋</span>
                </div>
                <h3 className="font-semibold text-lg">Requirements Extract</h3>
                <p className="text-gray-600">
                  Automatically extract structured requirements with priorities
                  and estimated costs.
                </p>
              </div>
            </div>

            {/* Feature 3 */}
            <div className="card">
              <div className="card-body space-y-4">
                <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                  <span className="text-2xl">⚖️</span>
                </div>
                <h3 className="font-semibold text-lg">Policy Compliance</h3>
                <p className="text-gray-600">
                  Get relevant policy snippets and compliance checks for your
                  procurement.
                </p>
              </div>
            </div>

            {/* Feature 4 */}
            <div className="card">
              <div className="card-body space-y-4">
                <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                  <span className="text-2xl">⚠️</span>
                </div>
                <h3 className="font-semibold text-lg">Risk Assessment</h3>
                <p className="text-gray-600">
                  Identify potential risks with severity levels and mitigation
                  strategies.
                </p>
              </div>
            </div>

            {/* Feature 5 */}
            <div className="card">
              <div className="card-body space-y-4">
                <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                  <span className="text-2xl">💡</span>
                </div>
                <h3 className="font-semibold text-lg">Smart Recommendations</h3>
                <p className="text-gray-600">
                  Receive prioritized action items with owners and timelines for
                  execution.
                </p>
              </div>
            </div>

            {/* Feature 6 */}
            <div className="card">
              <div className="card-body space-y-4">
                <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                  <span className="text-2xl">📊</span>
                </div>
                <h3 className="font-semibold text-lg">Confidence Scoring</h3>
                <p className="text-gray-600">
                  Get confidence scores for all analyses to gauge reliability of
                  recommendations.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="bg-gray-50 section">
        <div className="container max-w-3xl">
          <h2 className="text-3xl font-bold text-center mb-12">How It Works</h2>

          <div className="space-y-8">
            {/* Step 1 */}
            <div className="flex gap-6">
              <div className="flex-shrink-0">
                <div className="w-10 h-10 rounded-full bg-primary-600 text-white flex items-center justify-center font-bold">
                  1
                </div>
              </div>
              <div>
                <h3 className="font-semibold text-lg mb-2">Submit Request</h3>
                <p className="text-gray-600">
                  Fill out a simple form describing your procurement need. Include
                  title, description, budget, category, and urgency level.
                </p>
              </div>
            </div>

            {/* Step 2 */}
            <div className="flex gap-6">
              <div className="flex-shrink-0">
                <div className="w-10 h-10 rounded-full bg-primary-600 text-white flex items-center justify-center font-bold">
                  2
                </div>
              </div>
              <div>
                <h3 className="font-semibold text-lg mb-2">AI Analysis</h3>
                <p className="text-gray-600">
                  Our AI engine analyzes your request through 5 stages: normalization,
                  requirement extraction, policy retrieval, risk evaluation, and
                  recommendation generation.
                </p>
              </div>
            </div>

            {/* Step 3 */}
            <div className="flex gap-6">
              <div className="flex-shrink-0">
                <div className="w-10 h-10 rounded-full bg-primary-600 text-white flex items-center justify-center font-bold">
                  3
                </div>
              </div>
              <div>
                <h3 className="font-semibold text-lg mb-2">Get Results</h3>
                <p className="text-gray-600">
                  Review structured requirements, relevant policies, identified risks,
                  and prioritized recommendations with confidence scores and next steps.
                </p>
              </div>
            </div>

            {/* Step 4 */}
            <div className="flex gap-6">
              <div className="flex-shrink-0">
                <div className="w-10 h-10 rounded-full bg-primary-600 text-white flex items-center justify-center font-bold">
                  4
                </div>
              </div>
              <div>
                <h3 className="font-semibold text-lg mb-2">Take Action</h3>
                <p className="text-gray-600">
                  Use the recommendations to guide your procurement process. Follow
                  the action items, owners, and timelines provided by the AI.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="section bg-primary-600 text-white">
        <div className="container max-w-2xl text-center space-y-6">
          <h2 className="text-3xl font-bold">Ready to Transform Your Procurement?</h2>
          <p className="text-lg opacity-90">
            Get intelligent procurement recommendations powered by cutting-edge AI.
          </p>
          <Link href="/dashboard" className="btn-primary bg-white text-primary-600 hover:bg-gray-100 btn-large inline-block">
            Start Analyzing Now
          </Link>
        </div>
      </section>
    </div>
  );
}
