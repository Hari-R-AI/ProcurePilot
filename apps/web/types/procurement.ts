/**
 * Procurement-related TypeScript types
 * Aligned with backend FastAPI schemas (ProcurePilot v0.2.0)
 */

// ============================================================================
// Enums
// ============================================================================

export enum ProcurementUrgency {
  LOW = "LOW",
  MEDIUM = "MEDIUM",
  HIGH = "HIGH",
  CRITICAL = "CRITICAL",
}

export enum ProcurementCategory {
  IT_HARDWARE = "IT_HARDWARE",
  IT_SOFTWARE = "IT_SOFTWARE",
  OFFICE_SUPPLIES = "OFFICE_SUPPLIES",
  SERVICES = "SERVICES",
  CONSTRUCTION = "CONSTRUCTION",
  EQUIPMENT = "EQUIPMENT",
  CONSULTING = "CONSULTING",
  WORKS = "WORKS",
  OTHER = "OTHER",
}

export enum RiskSeverity {
  LOW = "LOW",
  MEDIUM = "MEDIUM",
  HIGH = "HIGH",
  CRITICAL = "CRITICAL",
}

export enum RecommendationPriority {
  P1 = "P1",
  P2 = "P2",
  P3 = "P3",
}

// ============================================================================
// Request Models
// ============================================================================

export interface ProcurementRequest {
  title: string;
  description: string;
  category: ProcurementCategory;
  budget?: number;
  budget_currency?: string;  // Default: INR
  urgency: ProcurementUrgency;
  department?: string;
  preferred_supplier?: string;
  vendor_gstin?: string;
  vendor_pan?: string;
  msme_registered: boolean;
  udyam_number?: string;
}

// ============================================================================
// Workflow Models (Internal — returned by backend)
// ============================================================================

export interface NormalizedRequest {
  original_title: string;
  original_description: string;
  normalized_title: string;
  normalized_description: string;
  category: string;
  budget_amount?: number;
  budget_currency: string;  // Default: INR
  urgency_level: string;
  department?: string;
  preferred_supplier?: string;
  vendor_gstin?: string;
  vendor_pan?: string;
  msme_registered: boolean;
  udyam_number?: string;
}

export interface Requirement {
  id: string;
  name: string;
  description: string;
  priority: "MUST_HAVE" | "SHOULD_HAVE" | "NICE_TO_HAVE";
  type: string;
}

export interface PolicyChunk {
  id: string;
  content: string;
  source: string;
  section?: string;
  similarity_score: number;
  metadata: Record<string, unknown>;
}

export interface RiskFlag {
  id: string;
  severity: RiskSeverity;
  category: string;
  description: string;
  policy_reference?: string;
  mitigation?: string;
}

export interface RecommendationItem {
  id: string;
  action: string;
  description: string;
  priority: RecommendationPriority;
  owner?: string;
  timeline?: string;
}

// ============================================================================
// Response Models
// ============================================================================

export interface AnalysisResponse {
  // Metadata
  request_id: string;
  trace_id: string;
  timestamp: string;
  processing_time_ms: number;

  // Summary
  summary: string;

  // Workflow outputs
  normalized_request: NormalizedRequest;
  extracted_requirements: Requirement[];
  policy_snippets: PolicyChunk[];
  risk_flags: RiskFlag[];

  // Recommendations
  recommendation_items: RecommendationItem[];
  recommendation_summary: string;

  // Confidence
  confidence_score: number;
  confidence_label: "LOW" | "MEDIUM" | "HIGH";
  confidence_reason: string;

  // Compliance
  compliance_status: "COMPLIANT" | "NON_COMPLIANT" | "PENDING_REVIEW";
  compliance_reasoning: string;

  // Approval Suggestion
  approval_suggestion?: ApprovalRouting | null;
}

export interface ApprovalRouting {
  level: "L1" | "L2" | "L3";
  role: string;
  reason: string;
}

// ============================================================================
// Request History Models
// ============================================================================

export type ProcurementRequestStatus =
  | "SUBMITTED"
  | "UNDER_REVIEW"
  | "ANALYZED"
  | "APPROVED"
  | "REJECTED";

export interface ProcurementRequestSummary {
  id: number;
  title: string;
  category: string;
  budget?: number;
  urgency: string;
  department?: string;
  created_at: string;
  status: ProcurementRequestStatus;
}

export interface ProcurementRequestDetail {
  id: number;
  title: string;
  description: string;
  category: string;
  budget?: number;
  urgency: string;
  department?: string;
  preferred_supplier?: string;
  vendor_gstin?: string;
  vendor_pan?: string;
  msme_registered: boolean;
  udyam_number?: string;
  created_at: string;
  status: ProcurementRequestStatus;
  latest_analysis?: AnalysisResponse | null;
}

// ============================================================================
// Vendor Management
// ============================================================================

export interface Vendor {
  id: number;
  legal_name: string;
  trade_name?: string | null;
  entity_type: string;
  gstin: string;
  pan_number: string;
  cin_number?: string | null;
  msme_registered: boolean;
  udyam_number?: string | null;
  msme_type?: "MICRO" | "SMALL" | "MEDIUM" | null;
  contact_email: string;
  contact_phone?: string | null;
  address: string;
  compliance_status: "PENDING" | "VERIFIED" | "REJECTED";
  created_at: string;
  updated_at: string;
}

export interface VendorCreate {
  legal_name: string;
  trade_name?: string;
  entity_type: string;
  gstin: string;
  pan_number: string;
  cin_number?: string;
  msme_registered: boolean;
  udyam_number?: string;
  msme_type?: "MICRO" | "SMALL" | "MEDIUM";
  contact_email: string;
  contact_phone?: string;
  address: string;
}

export interface VendorListResponse {
  vendors: Vendor[];
  total: number;
}
// ============================================================================
// Error Models
// ============================================================================

export interface ErrorResponse {
  error: string;
  detail: string;
  request_id?: string;
  trace_id?: string;
}

// ============================================================================
// Health Check Models
// ============================================================================

export interface HealthResponse {
  status: "healthy" | "degraded" | "unhealthy";
  timestamp: string;
  version: string;
}

export interface ReadinessResponse {
  ready: boolean;
  database: boolean;
  llm_service: boolean;
  checks: Record<string, boolean>;
  timestamp: string;
}

// ============================================================================
// Component-specific Types
// ============================================================================

export interface FormState {
  title: string;
  description: string;
  category: ProcurementCategory;
  budget?: number;
  urgency: ProcurementUrgency;
  department?: string;
  preferred_supplier?: string;
}

export interface LoadingState {
  isLoading: boolean;
  progress?: number;
  message?: string;
}

export interface ApiError {
  message: string;
  code?: string;
  requestId?: string;
}

// ============================================================================
// Budget / Currency Helpers
// ============================================================================

/**
 * Format a budget amount for display.
 * Defaults to INR formatting (₹ symbol with Indian number system).
 */
export function formatBudget(
  amount: number | undefined,
  currency: string = "INR"
): string {
  if (amount == null) return "—";
  const locale = currency === "INR" ? "en-IN" : "en-US";
  return new Intl.NumberFormat(locale, {
    style: "currency",
    currency,
    maximumFractionDigits: 0,
  }).format(amount);
}

/**
 * Get the status badge colour class for a procurement request status.
 */
export function getStatusColor(status: ProcurementRequestStatus): string {
  switch (status) {
    case "SUBMITTED":     return "badge-primary";
    case "UNDER_REVIEW":  return "badge-warning";
    case "ANALYZED":      return "badge-primary";
    case "APPROVED":      return "badge-success";
    case "REJECTED":      return "badge-danger";
    default:              return "badge-primary";
  }
}
