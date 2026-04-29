import {
  CampaignRunRequest,
  EvaluatedCampaignResult,
  ReadinessResponse,
  ReportExportFormat,
  SavedCampaignRecord,
  SavedCampaignSummary,
  WorkflowCatalogResponse
} from "@/types/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1";

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

async function readErrorMessage(response: Response): Promise<string> {
  let message = `Request failed with status ${response.status}`;
  try {
    const payload = (await response.json()) as { detail?: string };
    if (payload.detail) {
      message = payload.detail;
    }
  } catch {
    // Keep fallback message if backend did not return JSON.
  }
  return message;
}

function filenameFromDisposition(value: string | null, fallback: string): string {
  if (!value) {
    return fallback;
  }

  const utf8Match = value.match(/filename\*=UTF-8''([^;]+)/i);
  if (utf8Match?.[1]) {
    return decodeURIComponent(utf8Match[1].trim());
  }

  const asciiMatch = value.match(/filename="?([^";]+)"?/i);
  return asciiMatch?.[1]?.trim() || fallback;
}

export function getWorkflowCatalog(): Promise<WorkflowCatalogResponse> {
  return request<WorkflowCatalogResponse>("/workflows/catalog", { cache: "no-store" });
}

export function getReadiness(): Promise<ReadinessResponse> {
  return fetch(`${API_BASE_URL}/health/readiness`, {
    cache: "no-store"
  }).then(async (response) => {
    if (response.status === 200 || response.status === 503) {
      return (await response.json()) as ReadinessResponse;
    }

    let message = `Request failed with status ${response.status}`;
    try {
      const payload = (await response.json()) as { detail?: string };
      if (payload.detail) {
        message = payload.detail;
      }
    } catch {
      // Keep fallback message.
    }
    throw new ApiError(message, response.status);
  });
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

export async function downloadCampaignReport(
  runId: string,
  format: ReportExportFormat
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/reports/campaigns/${runId}?format=${format}`, {
    cache: "no-store"
  });

  if (!response.ok) {
    throw new ApiError(await readErrorMessage(response), response.status);
  }

  const blob = await response.blob();
  const filename = filenameFromDisposition(
    response.headers.get("content-disposition"),
    `campaign-${runId}-report.${format}`
  );
  const url = window.URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  window.URL.revokeObjectURL(url);
}
