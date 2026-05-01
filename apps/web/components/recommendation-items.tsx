"use client";

import { getPriorityColor } from "@/lib/utils";
import type { RecommendationItem } from "@/types/procurement";

interface RecommendationItemsProps {
  items: RecommendationItem[];
  summary: string;
}

export default function RecommendationItems({
  items,
  summary,
}: RecommendationItemsProps) {
  // Sort by priority (P1 first)
  const sortedItems = [...items].sort((a, b) => {
    const priorityOrder = { P1: 0, P2: 1, P3: 2 };
    return (
      (priorityOrder[a.priority] || 999) - (priorityOrder[b.priority] || 999)
    );
  });

  return (
    <div className="card">
      <div className="card-body">
        <h3 className="font-semibold mb-3">Recommendations</h3>

        {/* Summary */}
        <div className="bg-primary-50 border border-primary-200 rounded-lg p-4 mb-6">
          <p className="text-sm text-gray-700 leading-relaxed">{summary}</p>
        </div>

        {/* Items */}
        <div className="space-y-4">
          {sortedItems.map((item, idx) => (
            <div
              key={item.id}
              className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className={`badge text-xs ${getPriorityColor(item.priority)}`}>
                      {item.priority}
                    </span>
                    <span className="text-xs text-gray-600">
                      Step {idx + 1}
                    </span>
                  </div>
                  <h4 className="font-semibold text-gray-900">{item.action}</h4>
                </div>
              </div>

              <p className="text-sm text-gray-700 mb-3">
                {item.description}
              </p>

              <div className="grid grid-cols-2 gap-3 text-xs">
                {item.owner && (
                  <div className="bg-gray-50 rounded p-2">
                    <p className="text-gray-600 font-medium">Owner</p>
                    <p className="text-gray-900">{item.owner}</p>
                  </div>
                )}
                {item.timeline && (
                  <div className="bg-gray-50 rounded p-2">
                    <p className="text-gray-600 font-medium">Timeline</p>
                    <p className="text-gray-900">{item.timeline}</p>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
