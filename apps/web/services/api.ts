/**
 * API Client Service
 * Handles all communication with ProcurePilot backend
 */

import type {
    AnalysisResponse,
    ErrorResponse,
    HealthResponse,
    ProcurementRequest,
    ProcurementRequestDetail,
    ProcurementRequestSummary,
    ReadinessResponse,
    Vendor,
    VendorCreate,
    VendorListResponse,
} from "@/types/procurement";
import axios, { AxiosError, AxiosInstance } from "axios";

// Configuration
const DEFAULT_API_BASE_URL = "http://localhost:8000";
const API_BASE_URL = (process.env.NEXT_PUBLIC_API_BASE_URL || DEFAULT_API_BASE_URL)
  .replace(/\/+$/, "");
const API_TIMEOUT = 60000; // 60 seconds

type ApiErrorKind = "network" | "backend" | "validation" | "unknown";

class ApiClientError extends Error {
  kind: ApiErrorKind;
  status?: number;
  code?: string;
  requestId?: string;
  traceId?: string;

  constructor(message: string, kind: ApiErrorKind, options?: {
    status?: number;
    code?: string;
    requestId?: string;
    traceId?: string;
  }) {
    super(message);
    this.name = "ApiClientError";
    this.kind = kind;
    this.status = options?.status;
    this.code = options?.code;
    this.requestId = options?.requestId;
    this.traceId = options?.traceId;
  }
}

const formatValidationDetail = (detail: unknown): string => {
  if (!Array.isArray(detail)) {
    return "Backend returned validation error";
  }

  const messages = detail
    .map((item) => {
      if (!item || typeof item !== "object") {
        return null;
      }
      const record = item as { loc?: unknown[]; msg?: string };
      const location = Array.isArray(record.loc)
        ? record.loc.join(".")
        : "field";
      return record.msg ? `${location}: ${record.msg}` : null;
    })
    .filter((msg): msg is string => Boolean(msg));

  return messages.length > 0
    ? messages.join("; ")
    : "Backend returned validation error";
};

const extractErrorInfo = (data: unknown): {
  message: string;
  code?: string;
  requestId?: string;
  traceId?: string;
  kind: ApiErrorKind;
} => {
  if (data && typeof data === "object") {
    const record = data as Record<string, unknown>;
    const error = record.error as Record<string, unknown> | undefined;
    const detail = record.detail;

    if (error?.detail && typeof error.detail === "string") {
      return {
        message: error.detail,
        code: typeof error.code === "string" ? error.code : undefined,
        requestId:
          typeof error.request_id === "string" ? error.request_id : undefined,
        traceId:
          typeof error.trace_id === "string" ? error.trace_id : undefined,
        kind: "backend",
      };
    }

    if (detail) {
      return {
        message: formatValidationDetail(detail),
        kind: "validation",
      };
    }
  }

  if (typeof data === "string" && data.trim().length > 0) {
    return { message: data, kind: "backend" };
  }

  return {
    message: "Unexpected response format",
    kind: "unknown",
  };
};

// Create axios instance
const axiosInstance: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor - add tracing headers
axiosInstance.interceptors.request.use((config) => {
  // Add request ID for tracing
  const requestId = `web-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  config.headers["X-Request-ID"] = requestId;
  return config;
});

// Response interceptor - handle errors
axiosInstance.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ErrorResponse>) => {
    if (!error.response) {
      const message =
        "Could not connect to backend. Check that the API is running.";
      const apiError = new ApiClientError(message, "network", {
        code: error.code,
      });

      if (process.env.NODE_ENV !== "production") {
        console.error("[API Error]", apiError);
      }

      return Promise.reject(apiError);
    }

    const { message, code, requestId, traceId, kind } = extractErrorInfo(
      error.response.data
    );
    const apiError = new ApiClientError(message, kind, {
      status: error.response.status,
      code,
      requestId,
      traceId,
    });

    if (process.env.NODE_ENV !== "production") {
      console.error("[API Error]", apiError);
    }

    return Promise.reject(apiError);
  }
);

// ============================================================================
// Procurement API
// ============================================================================

export const api = {
  /**
   * Procurement Analysis Endpoints
   */
  procurement: {
    /**
     * Analyze a procurement request
     * POST /api/v1/procurement/analyze
     */
    async analyze(request: ProcurementRequest): Promise<AnalysisResponse> {
      // Backend route can be adjusted here if the API prefix changes.
      const response = await axiosInstance.post<AnalysisResponse>(
        "/api/v1/procurement/analyze",
        request
      );
      return response.data;
    },

    /**
     * List submitted requests
     * GET /api/v1/procurement/requests
     */
    async getSubmittedRequests(): Promise<ProcurementRequestSummary[]> {
      const response = await axiosInstance.get<ProcurementRequestSummary[]>(
        "/api/v1/procurement/requests"
      );
      return response.data;
    },

    /**
     * Get submitted request detail
     * GET /api/v1/procurement/requests/{id}
     */
    async getSubmittedRequestById(
      id: number
    ): Promise<ProcurementRequestDetail> {
      const response = await axiosInstance.get<ProcurementRequestDetail>(
        `/api/v1/procurement/requests/${id}`
      );
      return response.data;
    },

    /**
     * Update and re-analyze a procurement request
     * PUT /api/v1/procurement/requests/{id}
     */
    async update(id: number, request: ProcurementRequest): Promise<AnalysisResponse> {
      const response = await axiosInstance.put<AnalysisResponse>(
        `/api/v1/procurement/requests/${id}`,
        request
      );
      return response.data;
    },

    /**
     * Delete a procurement request
     * DELETE /api/v1/procurement/requests/{id}
     */
    async delete(id: number): Promise<void> {
      await axiosInstance.delete(`/api/v1/procurement/requests/${id}`);
    },

    /**
     * Download a PDF report of the procurement request
     * GET /api/v1/procurement/requests/{id}/report.pdf
     */
    async downloadReport(id: number): Promise<void> {
      const response = await axiosInstance.get(
        `/api/v1/procurement/requests/${id}/report.pdf`,
        {
          responseType: "blob",
        }
      );
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `Procurement_Report_${id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    },
  },

  /**
   * Vendor Management Endpoints
   */
  vendors: {
    async onboard(vendor: VendorCreate): Promise<Vendor> {
      const response = await axiosInstance.post<Vendor>("/api/v1/vendors", vendor);
      return response.data;
    },
    async list(skip = 0, limit = 50): Promise<VendorListResponse> {
      const response = await axiosInstance.get<VendorListResponse>("/api/v1/vendors", { params: { skip, limit } });
      return response.data;
    },
    async getById(id: number): Promise<Vendor> {
      const response = await axiosInstance.get<Vendor>(`/api/v1/vendors/${id}`);
      return response.data;
    },
  },

  /**
   * Health Check Endpoints
   */
  health: {
    /**
     * Check if API is alive
     * GET /api/v1/health/live
     */
    async liveness(): Promise<HealthResponse> {
      const response = await axiosInstance.get<HealthResponse>(
        "/api/v1/health/live"
      );
      return response.data;
    },

    /**
     * Check if API is ready
     * GET /api/v1/health/ready
     */
    async readiness(): Promise<ReadinessResponse> {
      const response = await axiosInstance.get<ReadinessResponse>(
        "/api/v1/health/ready"
      );
      return response.data;
    },

    /**
     * Full health status
     * GET /api/v1/health
     */
    async status(): Promise<HealthResponse> {
      const response = await axiosInstance.get<HealthResponse>(
        "/api/v1/health"
      );
      return response.data;
    },
  },

  /**
   * Raw axios instance for custom requests
   */
  axios: axiosInstance,

  /**
   * Get current API base URL
   */
  getBaseUrl(): string {
    return API_BASE_URL;
  },

  /**
   * Check if API is available
   */
  async isAvailable(): Promise<boolean> {
    try {
      await this.health.liveness();
      return true;
    } catch {
      return false;
    }
  },
};

// Export types
export { ApiClientError };
export type {
    AnalysisResponse,
    ErrorResponse,
    ProcurementRequest,
    ProcurementRequestDetail,
    ProcurementRequestSummary
};

