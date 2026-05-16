import { saveCurrentJob } from "./storage";
import type { JobInput } from "./types";

type ExtractJobResponse = {
  job: JobInput | null;
};

function isJobInput(value: unknown): value is JobInput {
  if (!value || typeof value !== "object") return false;
  const candidate = value as Partial<JobInput>;
  return Boolean(candidate.source && (candidate.job_title || candidate.company_name || candidate.job_description));
}

export async function syncJobFromActiveTab(): Promise<JobInput> {
  if (typeof chrome === "undefined" || !chrome.tabs?.query) {
    throw new Error("Chrome tab access is unavailable.");
  }

  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab?.id) {
    throw new Error("No active tab found.");
  }

  let response: ExtractJobResponse | undefined;
  try {
    response = await chrome.tabs.sendMessage(tab.id, { type: "APPLYINTEL_EXTRACT_JOB" });
  } catch {
    throw new Error("Open or refresh a LinkedIn job page, then sync again.");
  }

  if (!isJobInput(response?.job)) {
    throw new Error("No job details were found on the active tab.");
  }

  await saveCurrentJob(response.job);
  return response.job;
}
