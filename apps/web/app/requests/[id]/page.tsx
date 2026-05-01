"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import RecommendationPanel from "@/components/recommendation-panel";
import { formatDate } from "@/lib/utils";
import { api, ApiClientError } from "@/services/api";
import type { ProcurementRequestDetail } from "@/types/procurement";

export default function RequestDetailPage() {
  const params = useParams();
  const requestId = Number(params?.id);
  const [detail, setDetail] = useState<ProcurementRequestDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!requestId || Number.isNaN(requestId)) {
      setError("Invalid request id.");
      setIsLoading(false);
      return;
    }

    let isMounted = true;

    const fetchDetail = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await api.procurement.getSubmittedRequestById(requestId);
        if (isMounted) {
          setDetail(data);
        }
      } catch (err: unknown) {
        if (!isMounted) {
          return;
        }
        if (err instanceof ApiClientError) {
          setError(err.message);
        } else if (err instanceof Error) {
          setError(err.message);
        } else {
          setError("Unable to load request details.");
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    fetchDetail();

    return () => {
      isMounted = false;
    };
  }, [requestId]);

  return (
    <div className="section">
      <div className="container max-w-6xl space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Request Detail</h1>
            <p className="text-sm text-gray-600">
              View the submitted request and its latest analysis.
            </p>
          </div>
          <Link href="/requests" className="text-primary-600 text-sm">
            Back to Requests
          </Link>
        </div>

        {isLoading && (
          <div className="card">
            <div className="card-body">
              <p className="text-gray-600">Loading request...</p>
            </div>
          </div>
        )}

        {!isLoading && error && (
          <div className="alert alert-danger">
            <p className="font-medium">Error</p>
            <p className="text-sm">{error}</p>
          </div>
        )}

        {!isLoading && !error && detail && (
          <>
            <div className="card">
              <div className="card-body">
                <h2 className="text-xl font-semibold mb-4">Request Summary</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-gray-500">Title</p>
                    <p className="text-gray-900 font-medium">{detail.title}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Category</p>
                    <p className="text-gray-900 font-medium">{detail.category}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Urgency</p>
                    <p className="text-gray-900 font-medium">{detail.urgency}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Department</p>
                    <p className="text-gray-900 font-medium">
                      {detail.department || "—"}
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-500">Budget</p>
                    <p className="text-gray-900 font-medium">
                      {detail.budget ? `$${detail.budget.toLocaleString()}` : "—"}
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-500">Created</p>
                    <p className="text-gray-900 font-medium">
                      {formatDate(detail.created_at)}
                    </p>
                  </div>
                  <div className="md:col-span-2">
                    <p className="text-gray-500">Description</p>
                    <p className="text-gray-900 font-medium">
                      {detail.description}
                    </p>
                  </div>
                  {detail.preferred_supplier && (
                    <div>
                      <p className="text-gray-500">Preferred Supplier</p>
                      <p className="text-gray-900 font-medium">
                        {detail.preferred_supplier}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {detail.latest_analysis ? (
              <RecommendationPanel response={detail.latest_analysis} />
            ) : (
              <div className="card">
                <div className="card-body text-gray-600">
                  No analysis is available for this request yet.
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
