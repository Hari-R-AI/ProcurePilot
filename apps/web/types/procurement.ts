/**
 * Procurement-related TypeScript types
 * Aligned with backend FastAPI schemas
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
  urgency: ProcurementUrgency;
  department?: string;
  preferred_supplier?: string;
}

// ============================================================================
// Workflow Models (Internal)
// ============================================================================

export interface NormalizedRequest {
  original_title: string;
  original_description: string;
  normalized_title: string;
  normalized_description: string;
  category: string;
  budget_amount?: number;
  budget_currency: string;
  urgency_level: string;
  department?: string;
  preferred_supplier?: string;
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
  confidence_score: number;
  confidence_label: "LOW" | "MEDIUM" | "HIGH";
  confidence_reason: string;

  // Metadata
  processing_time_ms: number;
  request_id: string;
  trace_id: string;
  timestamp: string;
}

// ============================================================================
// Request History Models
// ============================================================================

export type ProcurementRequestStatus = "SUBMITTED" | "ANALYZED";

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
  created_at: string;
  status: ProcurementRequestStatus;
  latest_analysis?: AnalysisResponse | null;
}

// ============================================================================
// Error Models
// ============================================================================

export interface ErrorResponse {
  error: {
    code: string;
    detail: string;
    request_id?: string;
    trace_id?: string;
  };
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
