"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api } from "@/services/api";
import type { ProcurementRequestDetail, ProcurementRequest } from "@/types/procurement";
import { formatINR, formatDate } from "@/lib/utils";
import RecommendationPanel from "@/components/recommendation-panel";
import ProcurementRequestForm from "@/components/procurement-request-form";

export default function RequestDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = Number(params.id);

  const [request, setRequest] = useState<ProcurementRequestDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);

  useEffect(() => {
    if (isNaN(id)) {
      setError("Invalid Request ID");
      setIsLoading(false);
      return;
    }

    async function loadRequest() {
      try {
        const data = await api.procurement.getSubmittedRequestById(id);
        setRequest(data);
      } catch (err: any) {
        setError(err.message || "Failed to load request detail.");
      } finally {
        setIsLoading(false);
      }
    }
    loadRequest();
  }, [id]);

  const handleDelete = async () => {
    if (!confirm("Are you sure you want to delete this request?")) return;
    setIsDeleting(true);
    try {
      await api.procurement.delete(id);
      router.push("/requests");
    } catch (err: any) {
      alert("Failed to delete request: " + err.message);
      setIsDeleting(false);
    }
  };

  const handleDownloadReport = async () => {
    setIsDownloading(true);
    try {
      await api.procurement.downloadReport(id);
    } catch (err: any) {
      alert("Failed to download report: " + err.message);
    } finally {
      setIsDownloading(false);
    }
  };

  const handleUpdate = async (updatedData: ProcurementRequest) => {
    setIsLoading(true);
    setError(null);
    try {
      await api.procurement.update(id, updatedData);
      const data = await api.procurement.getSubmittedRequestById(id);
      setRequest(data);
      setIsEditing(false);
    } catch (err: any) {
      setError(err.message || "Failed to update request.");
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "SUBMITTED":
        return <span className="bg-gray-100 text-gray-800 px-3 py-1 rounded-full text-sm font-medium">Submitted</span>;
      case "UNDER_REVIEW":
        return <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">Under Review</span>;
      case "ANALYZED":
        return <span className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm font-medium">Analyzed</span>;
      case "APPROVED":
        return <span className="bg-success-100 text-success-800 px-3 py-1 rounded-full text-sm font-medium">Approved</span>;
      case "REJECTED":
        return <span className="bg-danger-100 text-danger-800 px-3 py-1 rounded-full text-sm font-medium">Rejected</span>;
      default:
        return <span className="bg-gray-100 text-gray-800 px-3 py-1 rounded-full text-sm font-medium">{status.replace("_", " ")}</span>;
    }
  };

  if (isLoading && !request) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-pulse">
        <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
        <div className="h-4 bg-gray-200 rounded w-1/2 mb-8"></div>
        <div className="space-y-4">
          <div className="h-40 bg-gray-200 rounded w-full"></div>
          <div className="h-64 bg-gray-200 rounded w-full"></div>
        </div>
      </div>
    );
  }

  if (error || !request) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-danger-50 text-danger-800 p-4 rounded-md">
          {error || "Request not found."}
        </div>
        <button onClick={() => router.push("/requests")} className="mt-4 text-primary-600 hover:underline">
          &larr; Back to Requests
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-6">
        <button onClick={() => router.push("/requests")} className="text-sm text-gray-500 hover:text-gray-900 mb-4 inline-block">
          &larr; Back to Requests
        </button>
        <div className="md:flex md:items-center md:justify-between">
          <div className="min-w-0 flex-1">
            <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl sm:tracking-tight">
              {request.title}
            </h2>
            <div className="mt-1 flex flex-col sm:mt-0 sm:flex-row sm:flex-wrap sm:space-x-6 text-sm text-gray-500">
              <div className="mt-2 flex items-center">
                ID: #{request.id}
              </div>
              <div className="mt-2 flex items-center">
                Date: {formatDate(request.created_at)}
              </div>
              <div className="mt-2 flex items-center">
                Category: {request.category}
              </div>
            </div>
          </div>
          <div className="mt-4 flex flex-wrap md:ml-4 md:mt-0 gap-3 items-center">
            {getStatusBadge(request.status)}
            <button 
              onClick={handleDownloadReport}
              disabled={isDownloading}
              className="text-sm bg-primary-600 text-white px-3 py-1 rounded hover:bg-primary-700 disabled:opacity-50 transition"
            >
              {isDownloading ? "Downloading..." : "Download PDF"}
            </button>
            <button 
              onClick={() => setIsEditing(!isEditing)}
              className="text-sm border border-gray-300 bg-white px-3 py-1 rounded hover:bg-gray-50 transition"
            >
              {isEditing ? "Cancel" : "Modify"}
            </button>
            <button 
              onClick={handleDelete}
              disabled={isDeleting}
              className="text-sm bg-danger-600 text-white px-3 py-1 rounded hover:bg-danger-700 disabled:opacity-50 transition"
            >
              {isDeleting ? "Deleting..." : "Delete"}
            </button>
          </div>
        </div>
      </div>

      {isEditing ? (
        <div className="bg-white shadow sm:rounded-lg border border-gray-200 p-6 max-w-3xl">
          <h3 className="text-lg font-medium mb-6">Modify Request</h3>
          <ProcurementRequestForm 
            initialData={request as unknown as ProcurementRequest} 
            onSubmit={handleUpdate}
            submitLabel="Update Request"
            isLoading={isLoading}
          />
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column: Original Request Details */}
          <div className="lg:col-span-1 space-y-6">
            <div className="bg-white shadow sm:rounded-lg border border-gray-200">
              <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
                <h3 className="text-base font-semibold leading-6 text-gray-900">Request Information</h3>
              </div>
              <div className="border-t border-gray-100">
                <dl className="divide-y divide-gray-100">
                  <div className="px-4 py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                    <dt className="text-sm font-medium text-gray-900">Description</dt>
                    <dd className="mt-1 text-sm leading-6 text-gray-700 sm:col-span-2">{request.description}</dd>
                  </div>
                  <div className="px-4 py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                    <dt className="text-sm font-medium text-gray-900">Budget</dt>
                    <dd className="mt-1 text-sm leading-6 text-gray-700 sm:col-span-2">
                      {request.budget ? formatINR(request.budget) : "Not specified"}
                    </dd>
                  </div>
                  <div className="px-4 py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                    <dt className="text-sm font-medium text-gray-900">Urgency</dt>
                    <dd className="mt-1 text-sm leading-6 text-gray-700 sm:col-span-2">{request.urgency}</dd>
                  </div>
                  {request.department && (
                    <div className="px-4 py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                      <dt className="text-sm font-medium text-gray-900">Department</dt>
                      <dd className="mt-1 text-sm leading-6 text-gray-700 sm:col-span-2">{request.department}</dd>
                    </div>
                  )}
                  {request.preferred_supplier && (
                    <div className="px-4 py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                      <dt className="text-sm font-medium text-gray-900">Supplier</dt>
                      <dd className="mt-1 text-sm leading-6 text-gray-700 sm:col-span-2">{request.preferred_supplier}</dd>
                    </div>
                  )}
                  {request.vendor_gstin && (
                    <div className="px-4 py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                      <dt className="text-sm font-medium text-gray-900">Supplier GSTIN</dt>
                      <dd className="mt-1 text-sm leading-6 text-gray-700 sm:col-span-2 font-mono">{request.vendor_gstin}</dd>
                    </div>
                  )}
                </dl>
              </div>
            </div>
          </div>

          {/* Right Column: AI Analysis */}
          <div className="lg:col-span-2">
            {request.latest_analysis ? (
              <RecommendationPanel response={request.latest_analysis} />
            ) : (
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center text-gray-500">
                No analysis data available for this request.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
