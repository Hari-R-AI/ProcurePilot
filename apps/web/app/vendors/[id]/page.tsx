"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api } from "@/services/api";
import type { Vendor } from "@/types/procurement";
import { formatDate } from "@/lib/utils";

export default function VendorDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = Number(params.id);

  const [vendor, setVendor] = useState<Vendor | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isNaN(id)) {
      setError("Invalid Vendor ID");
      setIsLoading(false);
      return;
    }

    async function loadVendor() {
      try {
        const data = await api.vendors.getById(id);
        setVendor(data);
      } catch (err: any) {
        setError(err.message || "Failed to load vendor details.");
      } finally {
        setIsLoading(false);
      }
    }
    loadVendor();
  }, [id]);

  const getComplianceBadge = (status: string) => {
    switch (status) {
      case "VERIFIED":
        return <span className="bg-success-100 text-success-800 px-3 py-1 rounded-full text-sm font-medium">Verified</span>;
      case "PENDING":
        return <span className="bg-warning-100 text-warning-800 px-3 py-1 rounded-full text-sm font-medium">Pending Verification</span>;
      case "REJECTED":
        return <span className="bg-danger-100 text-danger-800 px-3 py-1 rounded-full text-sm font-medium">Rejected</span>;
      default:
        return <span className="bg-gray-100 text-gray-800 px-3 py-1 rounded-full text-sm font-medium">{status}</span>;
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-pulse">
        <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
        <div className="h-40 bg-gray-200 rounded w-full"></div>
      </div>
    );
  }

  if (error || !vendor) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-danger-50 text-danger-800 p-4 rounded-md">
          {error || "Vendor not found."}
        </div>
        <button onClick={() => router.push("/vendors")} className="mt-4 text-primary-600 hover:underline">
          &larr; Back to Vendors
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-6">
        <button onClick={() => router.push("/vendors")} className="text-sm text-gray-500 hover:text-gray-900 mb-4 inline-block">
          &larr; Back to Registry
        </button>
        <div className="md:flex md:items-center md:justify-between">
          <div className="min-w-0 flex-1">
            <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl sm:tracking-tight">
              {vendor.legal_name}
            </h2>
            <div className="mt-1 flex flex-col sm:mt-0 sm:flex-row sm:flex-wrap sm:space-x-6 text-sm text-gray-500">
              <div className="mt-2 flex items-center">
                Vendor ID: #{vendor.id}
              </div>
              <div className="mt-2 flex items-center">
                Onboarded: {formatDate(vendor.created_at)}
              </div>
            </div>
          </div>
          <div className="mt-4 flex md:ml-4 md:mt-0">
            {getComplianceBadge(vendor.compliance_status)}
          </div>
        </div>
      </div>

      <div className="bg-white shadow sm:rounded-lg border border-gray-200">
        <div className="px-4 py-5 sm:px-6 border-b border-gray-200 flex justify-between items-center">
          <div>
            <h3 className="text-base font-semibold leading-6 text-gray-900">Vendor Profile</h3>
            <p className="mt-1 max-w-2xl text-sm text-gray-500">Legal and compliance details.</p>
          </div>
        </div>
        <div className="border-t border-gray-100">
          <dl className="divide-y divide-gray-100">
            {/* Business Info */}
            <div className="px-4 py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6 bg-gray-50">
              <dt className="text-sm font-medium text-gray-900">Trade Name (DBA)</dt>
              <dd className="mt-1 text-sm leading-6 text-gray-700 sm:col-span-2">{vendor.trade_name || "N/A"}</dd>
            </div>
            <div className="px-4 py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-900">Entity Type</dt>
              <dd className="mt-1 text-sm leading-6 text-gray-700 sm:col-span-2">{vendor.entity_type}</dd>
            </div>
            
            {/* Tax Details */}
            <div className="px-4 py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6 bg-gray-50">
              <dt className="text-sm font-medium text-gray-900">GSTIN</dt>
              <dd className="mt-1 text-sm leading-6 text-gray-700 sm:col-span-2 font-mono">{vendor.gstin}</dd>
            </div>
            <div className="px-4 py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-900">PAN Number</dt>
              <dd className="mt-1 text-sm leading-6 text-gray-700 sm:col-span-2 font-mono">{vendor.pan_number}</dd>
            </div>
            <div className="px-4 py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6 bg-gray-50">
              <dt className="text-sm font-medium text-gray-900">CIN Number</dt>
              <dd className="mt-1 text-sm leading-6 text-gray-700 sm:col-span-2 font-mono">{vendor.cin_number || "N/A"}</dd>
            </div>

            {/* MSME Details */}
            <div className="px-4 py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-900">MSME Registered</dt>
              <dd className="mt-1 text-sm leading-6 text-gray-700 sm:col-span-2">
                {vendor.msme_registered ? "Yes" : "No"}
              </dd>
            </div>
            {vendor.msme_registered && (
              <>
                <div className="px-4 py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6 bg-gray-50">
                  <dt className="text-sm font-medium text-gray-900">Udyam Registration</dt>
                  <dd className="mt-1 text-sm leading-6 text-gray-700 sm:col-span-2 font-mono">
                    {vendor.udyam_number || "Missing"}
                    {!vendor.udyam_number && (
                      <span className="ml-2 inline-flex items-center rounded-md bg-red-50 px-2 py-1 text-xs font-medium text-red-700 ring-1 ring-inset ring-red-600/10">
                        Action Required
                      </span>
                    )}
                  </dd>
                </div>
                <div className="px-4 py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                  <dt className="text-sm font-medium text-gray-900">MSME Classification</dt>
                  <dd className="mt-1 text-sm leading-6 text-gray-700 sm:col-span-2">{vendor.msme_type || "N/A"}</dd>
                </div>
              </>
            )}

            {/* Contact Details */}
            <div className="px-4 py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6 bg-gray-50">
              <dt className="text-sm font-medium text-gray-900">Contact Email</dt>
              <dd className="mt-1 text-sm leading-6 text-gray-700 sm:col-span-2">{vendor.contact_email}</dd>
            </div>
            <div className="px-4 py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-900">Contact Phone</dt>
              <dd className="mt-1 text-sm leading-6 text-gray-700 sm:col-span-2">{vendor.contact_phone || "N/A"}</dd>
            </div>
            <div className="px-4 py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6 bg-gray-50">
              <dt className="text-sm font-medium text-gray-900">Registered Address</dt>
              <dd className="mt-1 text-sm leading-6 text-gray-700 sm:col-span-2 whitespace-pre-wrap">{vendor.address}</dd>
            </div>

          </dl>
        </div>
      </div>
    </div>
  );
}
