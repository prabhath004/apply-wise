import type { JobInput } from "./types";

type CaptureResponse = {
  job?: JobInput;
  error?: string;
};

function isJobInput(value: unknown): value is JobInput {
  if (!value || typeof value !== "object") return false;
  const candidate = value as Partial<JobInput>;
  return Boolean(candidate.source && (candidate.job_title || candidate.company_name || candidate.job_description));
}

export async function syncJobFromActiveTab(): Promise<JobInput> {
  if (typeof chrome === "undefined" || !chrome.runtime?.sendMessage) {
    throw new Error("Chrome runtime access is unavailable.");
  }

  const response = await chrome.runtime.sendMessage({ type: "APPLYINTEL_CAPTURE_ACTIVE_JOB" }) as CaptureResponse;
  if (response.error) {
    throw new Error(response.error);
  }
  if (!isJobInput(response.job)) {
    throw new Error("No job details were found on the active tab.");
  }

  return response.job;
}
