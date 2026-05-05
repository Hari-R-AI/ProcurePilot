"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/services/api";
import type { VendorCreate } from "@/types/procurement";

export default function VendorOnboardingPage() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState<VendorCreate>({
    legal_name: "",
    trade_name: "",
    entity_type: "Private Limited",
    gstin: "",
    pan_number: "",
    cin_number: "",
    msme_registered: false,
    udyam_number: "",
    msme_type: "SMALL",
    contact_email: "",
    contact_phone: "",
    address: "",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    const isCheckbox = type === "checkbox";
    
    setFormData((prev) => ({
      ...prev,
      [name]: isCheckbox ? (e.target as HTMLInputElement).checked : value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      // Clean up empty strings to undefined to match optional API fields
      const payload = { ...formData };
      if (!payload.trade_name) payload.trade_name = undefined;
      if (!payload.cin_number) payload.cin_number = undefined;
      if (!payload.udyam_number) payload.udyam_number = undefined;
      if (!payload.contact_phone) payload.contact_phone = undefined;
      if (!payload.msme_registered) payload.msme_type = undefined;

      const newVendor = await api.vendors.onboard(payload as VendorCreate);
      router.push(`/vendors/${newVendor.id}`);
    } catch (err: any) {
      setError(err.message || "Failed to onboard vendor.");
      window.scrollTo({ top: 0, behavior: "smooth" });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Vendor Onboarding</h1>
        <p className="mt-2 text-sm text-gray-600">
          Register a new vendor and validate their Indian compliance details (GST, PAN, MSME).
        </p>
      </div>

      {error && (
        <div className="mb-6 bg-danger-50 text-danger-800 p-4 rounded-md">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-8 bg-white shadow-sm ring-1 ring-gray-900/5 sm:rounded-xl md:col-span-2">
        <div className="px-4 py-6 sm:p-8">
          <div className="grid max-w-2xl grid-cols-1 gap-x-6 gap-y-8 sm:grid-cols-6">
            
            {/* Basic Info */}
            <div className="col-span-full border-b border-gray-200 pb-4 mb-4">
              <h2 className="text-base font-semibold leading-7 text-gray-900">Entity Details</h2>
            </div>

            <div className="sm:col-span-3">
              <label htmlFor="legal_name" className="block text-sm font-medium leading-6 text-gray-900">
                Legal Name *
              </label>
              <div className="mt-2">
                <input
                  type="text"
                  name="legal_name"
                  id="legal_name"
                  required
                  value={formData.legal_name}
                  onChange={handleChange}
                  className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                />
              </div>
            </div>

            <div className="sm:col-span-3">
              <label htmlFor="trade_name" className="block text-sm font-medium leading-6 text-gray-900">
                Trade Name (DBA)
              </label>
              <div className="mt-2">
                <input
                  type="text"
                  name="trade_name"
                  id="trade_name"
                  value={formData.trade_name}
                  onChange={handleChange}
                  className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                />
              </div>
            </div>

            <div className="sm:col-span-3">
              <label htmlFor="entity_type" className="block text-sm font-medium leading-6 text-gray-900">
                Entity Type *
              </label>
              <div className="mt-2">
                <select
                  id="entity_type"
                  name="entity_type"
                  value={formData.entity_type}
                  onChange={handleChange}
                  className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:max-w-xs sm:text-sm sm:leading-6"
                >
                  <option>Private Limited</option>
                  <option>Public Limited</option>
                  <option>LLP</option>
                  <option>Partnership</option>
                  <option>Proprietorship</option>
                  <option>Other</option>
                </select>
              </div>
            </div>

            {/* Compliance */}
            <div className="col-span-full border-b border-gray-200 pb-4 mt-8 mb-4">
              <h2 className="text-base font-semibold leading-7 text-gray-900">Indian Compliance</h2>
              <p className="mt-1 text-sm leading-6 text-gray-600">Enter tax and registration numbers.</p>
            </div>

            <div className="sm:col-span-3">
              <label htmlFor="gstin" className="block text-sm font-medium leading-6 text-gray-900">
                GSTIN *
              </label>
              <div className="mt-2">
                <input
                  type="text"
                  name="gstin"
                  id="gstin"
                  required
                  maxLength={15}
                  value={formData.gstin}
                  onChange={handleChange}
                  placeholder="15-character GSTIN"
                  className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6 font-mono uppercase"
                  style={{ textTransform: 'uppercase' }}
                />
              </div>
            </div>

            <div className="sm:col-span-3">
              <label htmlFor="pan_number" className="block text-sm font-medium leading-6 text-gray-900">
                PAN Number *
              </label>
              <div className="mt-2">
                <input
                  type="text"
                  name="pan_number"
                  id="pan_number"
                  required
                  maxLength={10}
                  value={formData.pan_number}
                  onChange={handleChange}
                  placeholder="10-character PAN"
                  className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6 font-mono uppercase"
                  style={{ textTransform: 'uppercase' }}
                />
              </div>
            </div>

            <div className="col-span-full">
              <div className="flex items-center gap-x-3">
                <div className="flex h-6 items-center">
                  <input
                    id="msme_registered"
                    name="msme_registered"
                    type="checkbox"
                    checked={formData.msme_registered}
                    onChange={handleChange}
                    className="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-600"
                  />
                </div>
                <div className="text-sm leading-6">
                  <label htmlFor="msme_registered" className="font-medium text-gray-900">
                    Registered under MSME
                  </label>
                  <p className="text-gray-500">Eligible for price preference under MSME Act.</p>
                </div>
              </div>
            </div>

            {formData.msme_registered && (
              <>
                <div className="sm:col-span-3">
                  <label htmlFor="udyam_number" className="block text-sm font-medium leading-6 text-gray-900">
                    Udyam Number *
                  </label>
                  <div className="mt-2">
                    <input
                      type="text"
                      name="udyam_number"
                      id="udyam_number"
                      required={formData.msme_registered}
                      value={formData.udyam_number}
                      onChange={handleChange}
                      placeholder="UDYAM-XX-00-0000000"
                      className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6 uppercase"
                    />
                  </div>
                </div>

                <div className="sm:col-span-3">
                  <label htmlFor="msme_type" className="block text-sm font-medium leading-6 text-gray-900">
                    MSME Classification
                  </label>
                  <div className="mt-2">
                    <select
                      id="msme_type"
                      name="msme_type"
                      value={formData.msme_type}
                      onChange={handleChange}
                      className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:max-w-xs sm:text-sm sm:leading-6"
                    >
                      <option value="MICRO">Micro</option>
                      <option value="SMALL">Small</option>
                      <option value="MEDIUM">Medium</option>
                    </select>
                  </div>
                </div>
              </>
            )}

            {/* Contact Details */}
            <div className="col-span-full border-b border-gray-200 pb-4 mt-8 mb-4">
              <h2 className="text-base font-semibold leading-7 text-gray-900">Contact Details</h2>
            </div>

            <div className="sm:col-span-3">
              <label htmlFor="contact_email" className="block text-sm font-medium leading-6 text-gray-900">
                Email Address *
              </label>
              <div className="mt-2">
                <input
                  type="email"
                  name="contact_email"
                  id="contact_email"
                  required
                  value={formData.contact_email}
                  onChange={handleChange}
                  className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                />
              </div>
            </div>

            <div className="sm:col-span-3">
              <label htmlFor="contact_phone" className="block text-sm font-medium leading-6 text-gray-900">
                Phone Number
              </label>
              <div className="mt-2">
                <input
                  type="text"
                  name="contact_phone"
                  id="contact_phone"
                  value={formData.contact_phone}
                  onChange={handleChange}
                  className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                />
              </div>
            </div>

            <div className="col-span-full">
              <label htmlFor="address" className="block text-sm font-medium leading-6 text-gray-900">
                Registered Address *
              </label>
              <div className="mt-2">
                <textarea
                  id="address"
                  name="address"
                  rows={3}
                  required
                  value={formData.address}
                  onChange={handleChange}
                  className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
                />
              </div>
            </div>

          </div>
        </div>
        <div className="flex items-center justify-end gap-x-6 border-t border-gray-900/10 px-4 py-4 sm:px-8 bg-gray-50">
          <button type="button" onClick={() => router.back()} className="text-sm font-semibold leading-6 text-gray-900">
            Cancel
          </button>
          <button
            type="submit"
            disabled={isSubmitting}
            className="rounded-md bg-primary-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600 disabled:opacity-50"
          >
            {isSubmitting ? "Saving..." : "Onboard Vendor"}
          </button>
        </div>
      </form>
    </div>
  );
}
