"use client";

import type { PolicyChunk } from "@/types/procurement";
import { useState } from "react";

interface PolicySnippetsProps {
  policies: PolicyChunk[];
}

export default function PolicySnippets({ policies }: PolicySnippetsProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  return (
    <div className="card">
      <div className="card-body">
        <h3 className="font-semibold mb-4">
          Relevant Policies ({policies.length})
        </h3>
        <div className="space-y-3">
          {policies.map((policy) => (
            <div
              key={policy.id}
              className="border border-gray-200 rounded-lg overflow-hidden"
            >
              <button
                onClick={() =>
                  setExpandedId(expandedId === policy.id ? null : policy.id)
                }
                className="w-full px-4 py-3 text-left hover:bg-gray-50 transition-colors flex items-center justify-between"
              >
                <div className="flex-1">
                  <p className="font-medium text-gray-900">
                    {policy.source}
                  </p>
                  {policy.section && (
                    <p className="text-xs text-gray-500 mt-1">
                      Section: {policy.section}
                    </p>
                  )}
                </div>
                <span
                  className={`text-gray-600 transition-transform ${
                    expandedId === policy.id ? "rotate-180" : ""
                  }`}
                >
                  ▼
                </span>
              </button>

              {expandedId === policy.id && (
                <div className="px-4 py-3 bg-gray-50 border-t border-gray-200">
                  <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">
                    {policy.content}
                  </p>
                  {policy.similarity_score !== undefined && (
                    <p className="text-xs text-gray-500 mt-3">
                      Similarity Score: {(policy.similarity_score * 100).toFixed(0)}%
                    </p>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
