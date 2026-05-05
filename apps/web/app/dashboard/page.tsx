"use client";

import ProcurementRequestForm from "@/components/procurement-request-form";
import RecommendationPanel from "@/components/recommendation-panel";
import { api, ApiClientError } from "@/services/api";
import type { AnalysisResponse, ProcurementRequest } from "@/types/procurement";
import Link from "next/link";
import { useState } from "react";

export default function DashboardPage() {
  const [response, setResponse] = useState<AnalysisResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const isDev = process.env.NODE_ENV !== "production";

  const getUiErrorMessage = (err: unknown): string => {
    if (err instanceof ApiClientError) {
      if (err.kind === "network") {
        return "Could not connect to backend. Make sure the API is running.";
      }

      if (err.kind === "validation") {
        return err.message || "Backend returned validation error.";
      }

      if (err.kind === "unknown") {
        return "Unexpected response format from backend.";
      }

      return err.message || "Backend returned an error.";
    }

    if (err instanceof Error) {
      return err.message;
    }

    return "An unexpected error occurred.";
  };

  const handleSubmit = async (request: ProcurementRequest) => {
    if (isDev) {
      console.debug("[ProcurePilot] Submitting request", request);
      console.debug("[ProcurePilot] API base URL", api.getBaseUrl());
    }

    setIsLoading(true);
    setError(null);

    try {
      const result = await api.procurement.analyze(request);
      if (isDev) {
        console.debug("[ProcurePilot] Analysis response", result);
      }
      setResponse(result);
    } catch (err: unknown) {
      const errorMsg = getUiErrorMessage(err);
      setError(errorMsg);
      if (isDev) {
        console.error("[ProcurePilot] Analysis error", err);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewAnalysis = () => {
    setResponse(null);
    setError(null);
  };

  return (
    <div className="section">
      <div className="container max-w-6xl">
        {response ? (
          // Results view
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <button
                onClick={handleNewAnalysis}
                className="text-primary-600 hover:text-primary-700 font-medium text-sm"
              >
                ← New Analysis
              </button>
              <Link href="/requests" className="btn-secondary text-sm">
                Go to Requests
              </Link>
            </div>
            <RecommendationPanel response={response} />
          </div>
        ) : (
          // Form view
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Form Section */}
            <div className="lg:col-span-1">
              <div className="card sticky top-20">
                <div className="card-body">
                  <h2 className="text-xl font-bold mb-6">Submit Request</h2>
                  <ProcurementRequestForm
                    onSubmit={handleSubmit}
                    isLoading={isLoading}
                    error={error || undefined}
                  />
                </div>
              </div>
            </div>

            {/* Info Section */}
            <div className="lg:col-span-2 space-y-6">
              {/* Instructions */}
              <div className="card">
                <div className="card-header">
                  <h3 className="font-semibold">How to Use</h3>
                </div>
                <div className="card-body space-y-4">
                  <ol className="space-y-3 list-decimal list-inside">
                    <li>
                      <span className="font-medium">Fill in the form</span> with
                      your procurement request details
                    </li>
                    <li>
                      <span className="font-medium">Include context</span> in the
                      description to help the AI understand your needs
                    </li>
                    <li>
                      <span className="font-medium">Submit</span> to analyze with
                      our AI engine
                    </li>
                    <li>
                      <span className="font-medium">Review results</span> including
                      extracted requirements, risks, and recommendations
                    </li>
                  </ol>
                </div>
              </div>

              {/* Tips */}
              <div className="card">
                <div className="card-header">
                  <h3 className="font-semibold">Tips for Better Results</h3>
                </div>
                <div className="card-body space-y-3">
                  <div className="flex gap-3">
                    <span className="text-primary-600 font-bold">✓</span>
                    <div>
                      <p className="font-medium">Be Specific</p>
                      <p className="text-sm text-gray-600">
                        Include details about requirements, constraints, and
                        business context
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-3">
                    <span className="text-primary-600 font-bold">✓</span>
                    <div>
                      <p className="font-medium">Set Realistic Budget</p>
                      <p className="text-sm text-gray-600">
                        If known, include estimated budget for cost-aware
                        recommendations
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-3">
                    <span className="text-primary-600 font-bold">✓</span>
                    <div>
                      <p className="font-medium">Indicate Urgency</p>
                      <p className="text-sm text-gray-600">
                        Select appropriate urgency level for timeline-aware
                        recommendations
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-3">
                    <span className="text-primary-600 font-bold">✓</span>
                    <div>
                      <p className="font-medium">Mention Preferences</p>
                      <p className="text-sm text-gray-600">
                        Include preferred suppliers or specific requirements if any
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* FAQ */}
              <div className="card">
                <div className="card-header">
                  <h3 className="font-semibold">FAQ</h3>
                </div>
                <div className="card-body space-y-4">
                  <div>
                    <p className="font-medium text-sm">
                      What do the confidence scores mean?
                    </p>
                    <p className="text-sm text-gray-600 mt-1">
                      Confidence indicates how certain the AI is about the analysis.
                      Higher scores mean more reliable recommendations. 80%+ is
                      highly confident.
                    </p>
                  </div>
                  <div>
                    <p className="font-medium text-sm">
                      How long does analysis take?
                    </p>
                    <p className="text-sm text-gray-600 mt-1">
                      Most analyses complete in 5-30 seconds depending on complexity
                      and system load.
                    </p>
                  </div>
                  <div>
                    <p className="font-medium text-sm">
                      Can I save my analyses?
                    </p>
                    <p className="text-sm text-gray-600 mt-1">
                      All analyses are stored on our secure backend with request and
                      trace IDs for later reference.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
