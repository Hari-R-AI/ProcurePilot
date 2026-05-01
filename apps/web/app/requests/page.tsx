"use client";

import RequestHistory from "@/components/request-history";
import { api, ApiClientError } from "@/services/api";
import type { ProcurementRequestSummary } from "@/types/procurement";
import { useEffect, useState } from "react";

export default function RequestsPage() {
  const [items, setItems] = useState<ProcurementRequestSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    const fetchRequests = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await api.procurement.getSubmittedRequests();
        if (isMounted) {
          setItems(data);
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
          setError("Unable to load procurement requests.");
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    fetchRequests();

    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <div className="section">
      <div className="container max-w-6xl space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Requests</h1>
          <p className="text-sm text-gray-600">
            Review previously submitted procurement requests and their analyses.
          </p>
        </div>

        {isLoading && (
          <div className="card">
            <div className="card-body">
              <p className="text-gray-600">Loading requests...</p>
            </div>
          </div>
        )}

        {!isLoading && error && (
          <div className="alert alert-danger">
            <p className="font-medium">Error</p>
            <p className="text-sm">{error}</p>
          </div>
        )}

        {!isLoading && !error && items.length === 0 && (
          <div className="card">
            <div className="card-body text-center text-gray-600">
              No procurement requests submitted yet.
            </div>
          </div>
        )}

        {!isLoading && !error && items.length > 0 && (
          <RequestHistory items={items} />
        )}
      </div>
    </div>
  );
}
