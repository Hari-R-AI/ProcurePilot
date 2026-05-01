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
}

const CATEGORIES: { value: ProcurementCategory; label: string }[] = [
  { value: "IT_HARDWARE", label: "IT Hardware" },
  { value: "IT_SOFTWARE", label: "IT Software" },
  { value: "OFFICE_SUPPLIES", label: "Office Supplies" },
  { value: "SERVICES", label: "Services" },
  { value: "CONSTRUCTION", label: "Construction" },
  { value: "EQUIPMENT", label: "Equipment" },
  { value: "CONSULTING", label: "Consulting" },
  { value: "OTHER", label: "Other" },
];

const URGENCIES: { value: ProcurementUrgency; label: string }[] = [
  { value: "LOW", label: "Low" },
  { value: "MEDIUM", label: "Medium" },
  { value: "HIGH", label: "High" },
  { value: "CRITICAL", label: "Critical" },
];

export default function ProcurementRequestForm({
  onSubmit,
  isLoading = false,
  error = undefined,
}: ProcurementRequestFormProps) {
  const [formData, setFormData] = useState<ProcurementRequest>({
    title: "",
    description: "",
    category: "IT_HARDWARE",
    budget: undefined,
    urgency: "MEDIUM",
    department: undefined,
    preferred_supplier: undefined,
  });

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >
  ) => {
    const { name, value, type } = e.target;

    setFormData((prev) => ({
      ...prev,
      [name]:
        type === "number" && value ? parseFloat(value) : value || undefined,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.title.trim() || !formData.description.trim()) {
      alert("Please fill in all required fields");
      return;
    }

    await onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Error message */}
      {error && (
        <div className="alert alert-danger">
          <p className="font-medium">Error</p>
          <p className="text-sm">{error}</p>
        </div>
      )}

      {/* Title */}
      <div>
        <label htmlFor="title" className="block text-sm font-medium mb-2">
          Request Title <span className="text-danger-600">*</span>
        </label>
        <input
          id="title"
          type="text"
          name="title"
          value={formData.title}
          onChange={handleChange}
          placeholder="e.g., Purchase new laptop for engineering team"
          maxLength={200}
          disabled={isLoading}
          required
        />
        <p className="text-xs text-gray-500 mt-1">
          {formData.title.length}/200 characters
        </p>
      </div>

      {/* Description */}
      <div>
        <label htmlFor="description" className="block text-sm font-medium mb-2">
          Request Description <span className="text-danger-600">*</span>
        </label>
        <textarea
          id="description"
          name="description"
          value={formData.description}
          onChange={handleChange}
          placeholder="Provide detailed information about the procurement request..."
          rows={6}
          disabled={isLoading}
          required
        />
        <p className="text-xs text-gray-500 mt-1">
          Describe the business need, requirements, and any constraints
        </p>
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

      {/* Budget */}
      <div>
        <label htmlFor="budget" className="block text-sm font-medium mb-2">
          Budget (USD)
        </label>
        <input
          id="budget"
          type="number"
          name="budget"
          value={formData.budget || ""}
          onChange={handleChange}
          placeholder="e.g., 50000"
          min="0"
          step="100"
          disabled={isLoading}
        />
        <p className="text-xs text-gray-500 mt-1">
          Leave blank if budget is unknown
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
              {urg.label}
            </option>
          ))}
        </select>
      </div>

      {/* Department */}
      <div>
        <label htmlFor="department" className="block text-sm font-medium mb-2">
          Department
        </label>
        <input
          id="department"
          type="text"
          name="department"
          value={formData.department || ""}
          onChange={handleChange}
          placeholder="e.g., Engineering"
          disabled={isLoading}
        />
      </div>

      {/* Preferred Supplier */}
      <div>
        <label
          htmlFor="preferred_supplier"
          className="block text-sm font-medium mb-2"
        >
          Preferred Supplier
        </label>
        <input
          id="preferred_supplier"
          type="text"
          name="preferred_supplier"
          value={formData.preferred_supplier || ""}
          onChange={handleChange}
          placeholder="e.g., Acme Corp"
          disabled={isLoading}
        />
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={isLoading}
        className={cn(
          "btn-primary w-full",
          isLoading && "opacity-50 cursor-not-allowed"
        )}
      >
        {isLoading ? (
          <>
            <span className="spinner mr-2"></span>
            Analyzing Request...
          </>
        ) : (
          "Analyze Request"
        )}
      </button>
    </form>
  );
}
