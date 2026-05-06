import { clsx, type ClassValue } from "clsx";

export function cn(...inputs: ClassValue[]): string {
  return clsx(inputs);
}

export function formatDate(value?: string | Date | null): string {
  if (!value) {
    return "—";
  }

  const date = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "—";
  }

  return date.toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function formatINR(amount?: number | null): string {
  if (amount === null || amount === undefined || Number.isNaN(amount)) {
    return "—";
  }

  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 2,
  }).format(amount);
}

export function getSeverityColor(severity?: string | null): string {
  switch (severity) {
    case "CRITICAL":
      return "bg-danger-50 border-danger-300 text-danger-900";
    case "HIGH":
      return "bg-warning-50 border-warning-300 text-warning-900";
    case "MEDIUM":
      return "bg-primary-50 border-primary-300 text-primary-900";
    case "LOW":
      return "bg-success-50 border-success-300 text-success-900";
    default:
      return "bg-gray-50 border-gray-200 text-gray-900";
  }
}

export function getPriorityColor(priority?: string | null): string {
  switch (priority) {
    case "P1":
      return "bg-danger-100 text-danger-800";
    case "P2":
      return "bg-warning-100 text-warning-800";
    case "P3":
      return "bg-primary-100 text-primary-800";
    default:
      return "bg-gray-100 text-gray-800";
  }
}
import { clsx, type ClassValue } from "clsx";

export function cn(...inputs: ClassValue[]): string {
  return clsx(inputs);
}

export function formatDate(value?: string | Date | null): string {
  if (!value) {
    return "—";
  }

  const date = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "—";
  }

  return date.toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function formatINR(amount?: number | null): string {
  if (amount === null || amount === undefined || Number.isNaN(amount)) {
    return "—";
  }

  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 2,
  }).format(amount);
}

export function getSeverityColor(severity?: string | null): string {
  switch (severity) {
    case "CRITICAL":
      return "bg-danger-50 border-danger-300 text-danger-900";
    case "HIGH":
      return "bg-warning-50 border-warning-300 text-warning-900";
    case "MEDIUM":
      return "bg-primary-50 border-primary-300 text-primary-900";
    case "LOW":
      return "bg-success-50 border-success-300 text-success-900";
    default:
      return "bg-gray-50 border-gray-200 text-gray-900";
  }
}

export function getPriorityColor(priority?: string | null): string {
  switch (priority) {
    case "P1":
      return "bg-danger-100 text-danger-800";
    case "P2":
      return "bg-warning-100 text-warning-800";
    case "P3":
      return "bg-primary-100 text-primary-800";
    default:
      return "bg-gray-100 text-gray-800";
  }
}
