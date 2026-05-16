import type {
  AnalyzeJobResponse,
  ExtensionSettings,
  JobInput,
  OutreachResponse,
  ResumeUploadResponse
} from "./types";

export class ApiError extends Error {
  constructor(
    message: string,
    public status?: number
  ) {
    super(message);
  }
}

async function parseResponse<T>(response: Response): Promise<T> {
  const text = await response.text();
  const payload = text ? JSON.parse(text) : {};
  if (!response.ok) {
    const detail = payload.detail ?? payload;
    throw new ApiError(detail.message ?? "Request failed", response.status);
  }
  return payload as T;
}

function headers(settings: ExtensionSettings): HeadersInit {
  const result: HeadersInit = { Accept: "application/json" };
  if (settings.openaiApiKey) {
    result["X-OpenAI-API-Key"] = settings.openaiApiKey;
  }
  return result;
}

export async function checkHealth(settings: ExtensionSettings): Promise<boolean> {
  try {
    const response = await fetch(`${settings.backendUrl}/health`, { headers: headers(settings) });
    return response.ok;
  } catch {
    return false;
  }
}

export async function saveBackendSettings(settings: ExtensionSettings): Promise<void> {
  const response = await fetch(`${settings.backendUrl}/settings`, {
    method: "POST",
    headers: { ...headers(settings), "Content-Type": "application/json" },
    body: JSON.stringify({
      openai_api_key: settings.openaiApiKey || null,
      openai_model: settings.openaiModel,
      embedding_model: settings.embeddingModel,
      persist_api_key: false
    })
  });
  await parseResponse(response);
}

export async function uploadResume(settings: ExtensionSettings, file: File): Promise<ResumeUploadResponse> {
  const form = new FormData();
  form.append("file", file);
  const response = await fetch(`${settings.backendUrl}/resumes/upload`, {
    method: "POST",
    headers: headers(settings),
    body: form
  });
  return parseResponse<ResumeUploadResponse>(response);
}

export async function analyzeJob(
  settings: ExtensionSettings,
  resumeId: string,
  job: JobInput
): Promise<AnalyzeJobResponse> {
  const response = await fetch(`${settings.backendUrl}/analysis/job`, {
    method: "POST",
    headers: { ...headers(settings), "Content-Type": "application/json" },
    body: JSON.stringify({ resume_id: resumeId, job })
  });
  return parseResponse<AnalyzeJobResponse>(response);
}

export async function generateOutreach(
  settings: ExtensionSettings,
  analysisId: string,
  contactId: string | null,
  tone: "concise" | "friendly" | "formal"
): Promise<OutreachResponse> {
  const response = await fetch(`${settings.backendUrl}/outreach/generate`, {
    method: "POST",
    headers: { ...headers(settings), "Content-Type": "application/json" },
    body: JSON.stringify({
      analysis_id: analysisId,
      contact_id: contactId,
      tone,
      channel: "email"
    })
  });
  return parseResponse<OutreachResponse>(response);
}
