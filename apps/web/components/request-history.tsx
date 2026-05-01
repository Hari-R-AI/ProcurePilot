import Link from "next/link";

import { formatDate } from "@/lib/utils";
import type { ProcurementRequestSummary } from "@/types/procurement";

interface RequestHistoryProps {
  items: ProcurementRequestSummary[];
}

const getStatusStyles = (status: ProcurementRequestSummary["status"]) => {
  if (status === "ANALYZED") {
    return "badge-success";
  }
  return "badge-warning";
};

export default function RequestHistory({ items }: RequestHistoryProps) {
  return (
    <div className="card">
      <div className="card-header flex items-center justify-between">
        <h3 className="font-semibold">Submitted Requests</h3>
        <span className="text-xs text-gray-500">{items.length} total</span>
      </div>
      <div className="card-body">
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead className="text-left text-gray-500 border-b">
              <tr>
                <th className="py-2 pr-4">Title</th>
                <th className="py-2 pr-4">Category</th>
                <th className="py-2 pr-4">Budget</th>
                <th className="py-2 pr-4">Urgency</th>
                <th className="py-2 pr-4">Department</th>
                <th className="py-2 pr-4">Created</th>
                <th className="py-2 pr-4">Status</th>
                <th className="py-2">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {items.map((item) => (
                <tr key={item.id} className="hover:bg-gray-50">
                  <td className="py-3 pr-4 font-medium text-gray-900">
                    {item.title}
                  </td>
                  <td className="py-3 pr-4 text-gray-600">{item.category}</td>
                  <td className="py-3 pr-4 text-gray-600">
                    {item.budget ? `$${item.budget.toLocaleString()}` : "—"}
                  </td>
                  <td className="py-3 pr-4 text-gray-600">{item.urgency}</td>
                  <td className="py-3 pr-4 text-gray-600">
                    {item.department || "—"}
                  </td>
                  <td className="py-3 pr-4 text-gray-600">
                    {formatDate(item.created_at)}
                  </td>
                  <td className="py-3 pr-4">
                    <span className={`badge ${getStatusStyles(item.status)}`}>
                      {item.status}
                    </span>
                  </td>
                  <td className="py-3">
                    <Link
                      href={`/requests/${item.id}`}
                      className={`text-sm font-medium ${
                        item.status === "ANALYZED"
                          ? "text-primary-600 hover:text-primary-700"
                          : "text-gray-400 cursor-not-allowed"
                      }`}
                      aria-disabled={item.status !== "ANALYZED"}
                      tabIndex={item.status === "ANALYZED" ? 0 : -1}
                    >
                      View Analysis
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
