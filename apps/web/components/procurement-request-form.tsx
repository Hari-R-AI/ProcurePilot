"use client";

import { cn } from "@/lib/utils";
import type {
  ProcurementCategory,
  ProcurementRequest,
  ProcurementUrgency,
} from "@/types/procurement";
import { useState } from "react";

interface ProcurementRequestFormProps {
  onSubmit: (request: ProcurementRequest) => Promise<void>;
  isLoading?: boolean;
  error?: string;
  initialData?: ProcurementRequest | null;
  submitLabel?: string;
}

const CATEGORIES: { value: ProcurementCategory; label: string }[] = [
  { value: "IT_HARDWARE", label: "IT Hardware" },
  { value: "IT_SOFTWARE", label: "IT Software" },
  { value: "OFFICE_SUPPLIES", label: "Office Supplies" },
  { value: "SERVICES", label: "Services" },
  { value: "CONSTRUCTION", label: "Construction" },
  { value: "EQUIPMENT", label: "Equipment" },
  { value: "CONSULTING", label: "Consulting" },
  { value: "WORKS", label: "Works Contract" },
  { value: "OTHER", label: "Other" },
];

const URGENCIES: { value: ProcurementUrgency; label: string; hint: string }[] = [
  { value: "LOW",      label: "Low",      hint: "No immediate deadline" },
  { value: "MEDIUM",   label: "Medium",   hint: "Needed within 1–4 weeks" },
  { value: "HIGH",     label: "High",     hint: "Needed within 1 week" },
  { value: "CRITICAL", label: "Critical", hint: "Immediate — operations at risk" },
];

interface FormErrors {
  title?: string;
  description?: string;
}

export default function ProcurementRequestForm({
  onSubmit,
  isLoading = false,
  error = undefined,
  initialData,
  submitLabel,
}: ProcurementRequestFormProps) {
  const [formData, setFormData] = useState<ProcurementRequest>(initialData || {
    title: "",
    description: "",
    category: "IT_HARDWARE",
    budget: undefined,
    urgency: "MEDIUM",
    department: undefined,
    preferred_supplier: undefined,
    vendor_gstin: undefined,
    vendor_pan: undefined,
    msme_registered: false,
    udyam_number: undefined,
  });

  // Inline validation errors — replaces alert()
  const [fieldErrors, setFieldErrors] = useState<FormErrors>({});

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >
  ) => {
    const { name, value, type } = e.target;

    const isCheckbox = type === "checkbox";

    setFormData((prev) => ({
      ...prev,
      [name]: isCheckbox
        ? (e.target as HTMLInputElement).checked
        : type === "number" && value
        ? parseFloat(value)
        : value || undefined,
    }));

    // Clear field error when user starts typing
    if (fieldErrors[name as keyof FormErrors]) {
      setFieldErrors((prev) => ({ ...prev, [name]: undefined }));
    }
  };

  const validate = (): boolean => {
    const errors: FormErrors = {};

    if (!formData.title.trim() || formData.title.trim().length < 3) {
      errors.title = "Title must be at least 3 characters.";
    }
    if (!formData.description.trim() || formData.description.trim().length < 10) {
      errors.description = "Description must be at least 10 characters.";
    }

    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) {
      return;  // Show inline errors — no alert()
    }

    await onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6" noValidate>
      {/* API / server error message */}
      {error && (
        <div className="alert alert-danger" role="alert">
          <p className="font-medium text-sm">⚠ Analysis Error</p>
          <p className="text-sm mt-1">{error}</p>
        </div>
      )}

      {/* Title */}
      <div>
        <label htmlFor="title" className="block text-sm font-medium mb-2">
          Request Title <span className="text-danger-600" aria-hidden="true">*</span>
        </label>
        <input
          id="title"
          type="text"
          name="title"
          value={formData.title}
          onChange={handleChange}
          placeholder="e.g., Purchase 10 laptops for engineering team"
          maxLength={200}
          disabled={isLoading}
          required
          aria-describedby={fieldErrors.title ? "title-error" : undefined}
          aria-invalid={!!fieldErrors.title}
        />
        {fieldErrors.title ? (
          <p id="title-error" className="text-xs text-danger-600 mt-1" role="alert">
            {fieldErrors.title}
          </p>
        ) : (
          <p className="text-xs text-gray-500 mt-1">
            {formData.title.length}/200 characters
          </p>
        )}
      </div>

      {/* Description */}
      <div>
        <label htmlFor="description" className="block text-sm font-medium mb-2">
          Request Description <span className="text-danger-600" aria-hidden="true">*</span>
        </label>
        <textarea
          id="description"
          name="description"
          value={formData.description}
          onChange={handleChange}
          placeholder="Describe the procurement need, specifications, and business justification..."
          rows={6}
          disabled={isLoading}
          required
          aria-describedby={fieldErrors.description ? "description-error" : "description-hint"}
          aria-invalid={!!fieldErrors.description}
        />
        {fieldErrors.description ? (
          <p id="description-error" className="text-xs text-danger-600 mt-1" role="alert">
            {fieldErrors.description}
          </p>
        ) : (
          <p id="description-hint" className="text-xs text-gray-500 mt-1">
            Include business need, technical requirements, and any constraints.
          </p>
        )}
      </div>

      {/* Category */}
      <div>
        <label htmlFor="category" className="block text-sm font-medium mb-2">
          Category
        </label>
        <select
          id="category"
          name="category"
          value={formData.category}
          onChange={handleChange}
          disabled={isLoading}
        >
          {CATEGORIES.map((cat) => (
            <option key={cat.value} value={cat.value}>
              {cat.label}
            </option>
          ))}
        </select>
      </div>

      {/* Budget (INR) */}
      <div>
        <label htmlFor="budget" className="block text-sm font-medium mb-2">
          Estimated Budget (₹ INR)
        </label>
        <div className="relative">
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 text-sm select-none">
            ₹
          </span>
          <input
            id="budget"
            type="number"
            name="budget"
            value={formData.budget || ""}
            onChange={handleChange}
            placeholder="e.g., 500000"
            min="0"
            step="1000"
            disabled={isLoading}
            className="pl-7"
          />
        </div>
        <p className="text-xs text-gray-500 mt-1">
          Leave blank if budget is not yet determined. GFR approval levels apply based on amount.
        </p>
      </div>

      {/* Urgency */}
      <div>
        <label htmlFor="urgency" className="block text-sm font-medium mb-2">
          Urgency Level
        </label>
        <select
          id="urgency"
          name="urgency"
          value={formData.urgency}
          onChange={handleChange}
          disabled={isLoading}
        >
          {URGENCIES.map((urg) => (
            <option key={urg.value} value={urg.value}>
              {urg.label} — {urg.hint}
            </option>
          ))}
        </select>
      </div>

      {/* Department */}
      <div>
        <label htmlFor="department" className="block text-sm font-medium mb-2">
          Requesting Department
        </label>
        <input
          id="department"
          type="text"
          name="department"
          value={formData.department || ""}
          onChange={handleChange}
          placeholder="e.g., Finance, IT Infrastructure, Operations"
          disabled={isLoading}
        />
      </div>

      {/* Preferred Supplier */}
      <div className="pt-4 border-t border-gray-200">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Supplier Details (Optional)</h3>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="sm:col-span-2">
            <label
              htmlFor="preferred_supplier"
              className="block text-sm font-medium mb-2"
            >
              Preferred Supplier Name
            </label>
            <input
              id="preferred_supplier"
              type="text"
              name="preferred_supplier"
              value={formData.preferred_supplier || ""}
              onChange={handleChange}
              placeholder="e.g., TCS, Infosys, or GeM-registered vendor"
              disabled={isLoading}
            />
            <p className="text-xs text-gray-500 mt-1">
              GeM-registered vendors receive preference under government procurement policy.
            </p>
          </div>

          <div>
            <label htmlFor="vendor_gstin" className="block text-sm font-medium mb-2">
              Supplier GSTIN
            </label>
            <input
              id="vendor_gstin"
              type="text"
              name="vendor_gstin"
              value={formData.vendor_gstin || ""}
              onChange={handleChange}
              placeholder="15-digit GSTIN"
              maxLength={15}
              disabled={isLoading}
            />
          </div>

          <div>
            <label htmlFor="vendor_pan" className="block text-sm font-medium mb-2">
              Supplier PAN
            </label>
            <input
              id="vendor_pan"
              type="text"
              name="vendor_pan"
              value={formData.vendor_pan || ""}
              onChange={handleChange}
              placeholder="10-digit PAN"
              maxLength={10}
              disabled={isLoading}
            />
          </div>

          <div className="sm:col-span-2 mt-2">
            <div className="flex items-center gap-3">
              <input
                id="msme_registered"
                type="checkbox"
                name="msme_registered"
                checked={formData.msme_registered}
                onChange={handleChange}
                disabled={isLoading}
                className="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
              />
              <label htmlFor="msme_registered" className="text-sm font-medium text-gray-700">
                Supplier is MSME Registered
              </label>
            </div>
            <p className="text-xs text-gray-500 mt-1 ml-7">
              MSME vendors are eligible for price preference under the MSME Act.
            </p>
          </div>

          {formData.msme_registered && (
            <div className="sm:col-span-2 ml-7 mt-2">
              <label htmlFor="udyam_number" className="block text-sm font-medium mb-2">
                Udyam Registration Number
              </label>
              <input
                id="udyam_number"
                type="text"
                name="udyam_number"
                value={formData.udyam_number || ""}
                onChange={handleChange}
                placeholder="e.g., UDYAM-MH-00-0000000"
                maxLength={20}
                disabled={isLoading}
              />
            </div>
          )}
        </div>
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={isLoading}
        id="analyze-submit-btn"
        className={cn(
          "btn-primary w-full",
          isLoading && "opacity-50 cursor-not-allowed"
        )}
      >
        {isLoading ? (
          <>
            <span className="spinner mr-2" aria-hidden="true" />
            Processing...
          </>
        ) : (
          submitLabel || "Analyse Procurement Request"
        )}
      </button>
    </form>
  );
}
