"use client";

import { formatDate } from "@/lib/utils";
import type { AnalysisResponse } from "@/types/procurement";
import PolicySnippets from "./policy-snippets";
import RecommendationItems from "./recommendation-items";
import RiskFlags from "./risk-flags";

interface RecommendationPanelProps {
  response: AnalysisResponse;
  onClose?: () => void;
}

export default function RecommendationPanel({
  response,
  onClose,
}: RecommendationPanelProps) {
  const confidencePercent = Math.round(response.confidence_score * 100);
  const formatPriority = (priority: string) =>
    priority.replace(/_/g, " ");

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-2xl font-bold">Analysis Results</h2>
          <p className="text-sm text-gray-600 mt-1">
            Request ID: {response.request_id}
          </p>
        </div>
        {onClose && (
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            ✕
          </button>
        )}
      </div>

      {/* Confidence Score */}
      <div className="card">
        <div className="card-body">
          <h3 className="font-semibold mb-4">Analysis Confidence</h3>
          <div className="flex items-end justify-between mb-4">
            <div className="flex-1">
              <div className="bg-gray-200 rounded-full h-3 mb-2 overflow-hidden">
                <div
                  className={`h-full transition-all ${
                    confidencePercent >= 80
                      ? "bg-success-600"
                      : confidencePercent >= 60
                        ? "bg-primary-600"
                        : confidencePercent >= 40
                          ? "bg-warning-600"
                          : "bg-danger-600"
                  }`}
                  style={{ width: `${confidencePercent}%` }}
                />
              </div>
            </div>
            <div className="ml-4 text-right">
              <div className="text-2xl font-bold">{confidencePercent}%</div>
              <p className="text-xs font-medium text-gray-700">
                {response.confidence_label}
              </p>
            </div>
          </div>
          <p className="text-sm text-gray-700 bg-gray-50 rounded p-2 mb-3">
            {response.confidence_reason}
          </p>
          <p className="text-xs text-gray-600">
            Processed in {response.processing_time_ms}ms on{" "}
            {formatDate(response.timestamp)}
          </p>
        </div>
      </div>

      {/* Summary */}
      <div className="card">
        <div className="card-body">
          <h3 className="font-semibold mb-3">Summary</h3>
          <p className="text-gray-700 leading-relaxed">
            {response.summary}
          </p>
        </div>
      </div>

      {/* Normalized Request */}
      <div className="card">
        <div className="card-body">
          <h3 className="font-semibold mb-4">Normalized Request</h3>
          <dl className="space-y-3">
            <div className="flex">
              <dt className="text-sm font-medium text-gray-600 w-32">Title</dt>
              <dd className="text-sm text-gray-900">
                {response.normalized_request.normalized_title}
              </dd>
            </div>
            <div className="flex">
              <dt className="text-sm font-medium text-gray-600 w-32">
                Category
              </dt>
              <dd className="text-sm text-gray-900">
                {response.normalized_request.category}
              </dd>
            </div>
            <div className="flex">
              <dt className="text-sm font-medium text-gray-600 w-32">
                Urgency
              </dt>
              <dd className="text-sm text-gray-900">
                {response.normalized_request.urgency_level}
              </dd>
            </div>
            {response.normalized_request.budget_amount && (
              <div className="flex">
                <dt className="text-sm font-medium text-gray-600 w-32">
                  Budget
                </dt>
                <dd className="text-sm text-gray-900">
                  ${response.normalized_request.budget_amount.toLocaleString()}
                </dd>
              </div>
            )}
            {response.normalized_request.department && (
              <div className="flex">
                <dt className="text-sm font-medium text-gray-600 w-32">
                  Department
                </dt>
                <dd className="text-sm text-gray-900">
                  {response.normalized_request.department}
                </dd>
              </div>
            )}
          </dl>
        </div>
      </div>

      {/* Extracted Requirements */}
      <div className="card">
        <div className="card-body">
          <h3 className="font-semibold mb-4">
            Extracted Requirements ({response.extracted_requirements.length})
          </h3>
          {response.extracted_requirements.length > 0 ? (
            <ul className="space-y-3">
              {response.extracted_requirements.map((req) => (
                <li key={req.id} className="border-l-4 border-primary-500 pl-4">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="font-medium text-gray-900">{req.name}</p>
                      <p className="text-sm text-gray-600 mt-1">
                        {req.description}
                      </p>
                    </div>
                    <span className="badge badge-primary text-xs">
                      {formatPriority(req.priority)}
                    </span>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-600 text-sm">No requirements extracted</p>
          )}
        </div>
      </div>

      {/* Policy Snippets */}
      {response.policy_snippets.length > 0 && (
        <PolicySnippets policies={response.policy_snippets} />
      )}

      {/* Risk Flags */}
      {response.risk_flags.length > 0 && (
        <RiskFlags risks={response.risk_flags} />
      )}

      {/* Recommendation Items */}
      {response.recommendation_items.length > 0 && (
        <RecommendationItems
          items={response.recommendation_items}
          summary={response.recommendation_summary}
        />
      )}

      {/* Metadata */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 text-xs text-gray-600 space-y-2">
        <div className="flex justify-between">
          <span>Trace ID:</span>
          <code className="bg-white px-2 py-1 rounded">{response.trace_id}</code>
        </div>
        <div className="flex justify-between">
          <span>Request ID:</span>
          <code className="bg-white px-2 py-1 rounded">
            {response.request_id}
          </code>
        </div>
        <div className="flex justify-between">
          <span>Processing Time:</span>
          <span>{response.processing_time_ms}ms</span>
        </div>
      </div>
    </div>
  );
}
