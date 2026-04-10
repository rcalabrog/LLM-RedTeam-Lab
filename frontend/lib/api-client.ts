import {
  CampaignRunRequest,
  EvaluatedCampaignResult,
  ReadinessResponse,
  SavedCampaignRecord,
  SavedCampaignSummary,
  WorkflowCatalogResponse
} from "@/types/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "/backend/api/v1";

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

interface FetchOptions extends RequestInit {
  cache?: RequestCache;
}

async function request<T>(path: string, options?: FetchOptions): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers ?? {})
    },
    ...options
  });

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;
    try {
      const payload = (await response.json()) as { detail?: string };
      if (payload.detail) {
        message = payload.detail;
      }
    } catch {
      // Keep fallback message if backend did not return JSON.
    }
    throw new ApiError(message, response.status);
  }

  return (await response.json()) as T;
}

export function getWorkflowCatalog(): Promise<WorkflowCatalogResponse> {
  return request<WorkflowCatalogResponse>("/workflows/catalog", { cache: "no-store" });
}

export function getReadiness(): Promise<ReadinessResponse> {
  return request<ReadinessResponse>("/health/readiness", { cache: "no-store" });
}

export function executeEvaluate(payload: CampaignRunRequest): Promise<EvaluatedCampaignResult> {
  return request<EvaluatedCampaignResult>("/workflows/execute-evaluate", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function executeEvaluateSave(payload: CampaignRunRequest): Promise<SavedCampaignRecord> {
  return request<SavedCampaignRecord>("/workflows/execute-evaluate-save", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function listSavedCampaigns(): Promise<SavedCampaignSummary[]> {
  return request<SavedCampaignSummary[]>("/storage/campaigns", { cache: "no-store" });
}

export function getSavedCampaign(runId: string): Promise<SavedCampaignRecord> {
  return request<SavedCampaignRecord>(`/storage/campaigns/${runId}`, { cache: "no-store" });
}
