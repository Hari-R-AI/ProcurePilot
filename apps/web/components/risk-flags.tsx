"use client";

import { getSeverityColor } from "@/lib/utils";
import type { RiskFlag } from "@/types/procurement";
import { useState } from "react";

interface RiskFlagsProps {
  risks: RiskFlag[];
}

export default function RiskFlags({ risks }: RiskFlagsProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  // Count by severity
  const criticalCount = risks.filter(r => r.severity === "CRITICAL").length;
  const highCount = risks.filter(r => r.severity === "HIGH").length;
  const mediumCount = risks.filter(r => r.severity === "MEDIUM").length;
  const lowCount = risks.filter(r => r.severity === "LOW").length;

  // Sort by severity
  const sortedRisks = [...risks].sort((a, b) => {
    const severityOrder = { CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3 };
    return (
      (severityOrder[a.severity] || 999) - (severityOrder[b.severity] || 999)
    );
  });

  return (
    <div className="card">
      <div className="card-body">
        <h3 className="font-semibold mb-4">Risk Assessment</h3>

        {/* Risk summary */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
          {criticalCount > 0 && (
            <div className="bg-danger-50 border border-danger-200 rounded-lg p-3 text-center">
              <div className="text-xl font-bold text-danger-700">
                {criticalCount}
              </div>
              <div className="text-xs text-danger-600">Critical</div>
            </div>
          )}
          {highCount > 0 && (
            <div className="bg-warning-50 border border-warning-200 rounded-lg p-3 text-center">
              <div className="text-xl font-bold text-warning-700">
                {highCount}
              </div>
              <div className="text-xs text-warning-600">High</div>
            </div>
          )}
          {mediumCount > 0 && (
            <div className="bg-primary-50 border border-primary-200 rounded-lg p-3 text-center">
              <div className="text-xl font-bold text-primary-700">
                {mediumCount}
              </div>
              <div className="text-xs text-primary-600">Medium</div>
            </div>
          )}
          {lowCount > 0 && (
            <div className="bg-success-50 border border-success-200 rounded-lg p-3 text-center">
              <div className="text-xl font-bold text-success-700">{lowCount}</div>
              <div className="text-xs text-success-600">Low</div>
            </div>
          )}
        </div>

        {/* Risk items */}
        <div className="space-y-2">
          {sortedRisks.map((risk) => (
            <div
              key={risk.id}
              className={`border rounded-lg overflow-hidden ${getSeverityColor(
                risk.severity
              )}`}
            >
              <button
                onClick={() =>
                  setExpandedId(expandedId === risk.id ? null : risk.id)
                }
                className="w-full px-4 py-3 text-left hover:opacity-80 transition-opacity flex items-center justify-between"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-sm">
                      {risk.severity}
                    </span>
                    <span className="text-xs opacity-75">{risk.category}</span>
                  </div>
                  <p className="text-sm font-medium mt-1">{risk.description}</p>
                </div>
                <span
                  className={`transition-transform ${
                    expandedId === risk.id ? "rotate-180" : ""
                  }`}
                >
                  ▼
                </span>
              </button>

              {expandedId === risk.id && (
                <div className="px-4 py-3 border-t opacity-90 space-y-2 text-sm">
                  {risk.policy_reference && (
                    <div>
                      <p className="font-semibold">Policy Reference:</p>
                      <p className="text-xs opacity-90">
                        {risk.policy_reference}
                      </p>
                    </div>
                  )}
                  {risk.mitigation && (
                    <div>
                      <p className="font-semibold">Mitigation:</p>
                      <p className="text-xs opacity-90">{risk.mitigation}</p>
                    </div>
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
