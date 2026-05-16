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

function extractLinkedInJobInPage(): JobInput | null {
  const titleSelectors = [
    ".job-details-jobs-unified-top-card__job-title",
    ".jobs-unified-top-card__job-title",
    ".jobs-search__job-details--container h1",
    "[data-test-job-title]",
    "h1"
  ];
  const companySelectors = [
    ".job-details-jobs-unified-top-card__company-name a",
    ".jobs-unified-top-card__company-name a",
    ".jobs-search__job-details--container a[href*='/company/']",
    "a[href*='/company/']"
  ];
  const locationSelectors = [
    ".job-details-jobs-unified-top-card__primary-description-container",
    ".job-details-jobs-unified-top-card__primary-description-container span",
    ".jobs-unified-top-card__bullet",
    ".jobs-unified-top-card__workplace-type",
    ".jobs-search__job-details--container [class*='primary-description']"
  ];
  const descriptionSelectors = [
    "#job-details",
    ".jobs-description",
    ".jobs-description__container",
    ".jobs-description__content",
    ".jobs-box__html-content",
    ".jobs-description-content__text",
    "[class*='jobs-description']"
  ];

  function clean(value: string | null | undefined): string {
    return value?.replace(/\s+/g, " ").trim() ?? "";
  }

  function visibleTextFromSelectors(selectors: string[]): string {
    for (const selector of selectors) {
      const candidates = Array.from(document.querySelectorAll(selector));
      const visible = candidates.find((candidate) => {
        if (!(candidate instanceof HTMLElement)) return true;
        const style = window.getComputedStyle(candidate);
        return style.display !== "none" && style.visibility !== "hidden";
      }) ?? candidates[0];
      const value = clean(visible?.textContent);
      if (value) return value;
    }
    return "";
  }

  function allTextFromSelectors(selectors: string[]): string {
    const values = selectors
      .flatMap((selector) => Array.from(document.querySelectorAll(selector)))
      .map((node) => clean(node.textContent))
      .filter(Boolean);
    return Array.from(new Set(values)).join("\n");
  }

  function titleFromDocument(): string {
    const title = clean(document.title)
      .replace(/\s+\|\s+LinkedIn.*$/i, "")
      .replace(/\s+-\s+LinkedIn.*$/i, "")
      .replace(/\s+at\s+.+$/i, "")
      .trim();
    if (!title || /linkedin/i.test(title) || title.length > 120) return "";
    return title;
  }

  function locationFromText(value: string): string {
    if (!value) return "";
    const withoutStatus = value
      .replace(/\b\d+\s+days?\s+ago\b/gi, "")
      .replace(/\bover\s+\d+\s+applicants\b/gi, "")
      .replace(/\bpromoted by hirer\b/gi, "")
      .replace(/\bactively reviewing applicants\b/gi, "");
    return clean(withoutStatus.split("·")[0]);
  }

  function descriptionFromPage(): string {
    const selected = allTextFromSelectors(descriptionSelectors);
    if (selected.length > 80) return selected;
    const body = clean(document.body?.innerText);
    const marker = body.toLowerCase().indexOf("about the job");
    if (marker >= 0) {
      return body.slice(marker).replace(/^about the job\s*/i, "").trim();
    }
    return selected;
  }

  const title = visibleTextFromSelectors(titleSelectors) || titleFromDocument();
  const company = visibleTextFromSelectors(companySelectors);
  const location = locationFromText(visibleTextFromSelectors(locationSelectors));
  const description = descriptionFromPage();

  if (!title && !company && !description) return null;

  return {
    source: "linkedin",
    job_title: title,
    company_name: company,
    location,
    job_url: window.location.href,
    job_description: description
  };
}

async function getActiveLinkedInTab(): Promise<chrome.tabs.Tab> {
  if (typeof chrome === "undefined" || !chrome.tabs?.query) {
    throw new Error("Chrome tab access is unavailable. Reload the extension.");
  }

  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab?.id) {
    throw new Error("No active tab found.");
  }
  if (tab.url && !tab.url.includes("linkedin.com/jobs")) {
    throw new Error("Open a LinkedIn job page, then sync again.");
  }
  return tab;
}

async function captureWithScripting(tabId: number): Promise<JobInput | null> {
  if (!chrome.scripting?.executeScript) return null;
  const [result] = await chrome.scripting.executeScript({
    target: { tabId },
    func: extractLinkedInJobInPage
  });
  return result?.result ?? null;
}

async function captureWithContentScript(tabId: number): Promise<JobInput | null> {
  const response = await chrome.tabs.sendMessage(tabId, { type: "APPLYINTEL_EXTRACT_JOB" }) as ExtractJobResponse;
  return response.job;
}

export async function syncJobFromActiveTab(): Promise<JobInput> {
  const tab = await getActiveLinkedInTab();
  const tabId = tab.id as number;
  let lastError: unknown = null;

  try {
    const job = await captureWithScripting(tabId);
    if (isJobInput(job)) {
      await saveCurrentJob(job);
      return job;
    }
  } catch (error) {
    lastError = error;
  }

  try {
    const job = await captureWithContentScript(tabId);
    if (isJobInput(job)) {
      await saveCurrentJob(job);
      return job;
    }
  } catch (error) {
    lastError = error;
  }

  if (lastError instanceof Error) {
    throw new Error(`Could not capture this LinkedIn page: ${lastError.message}`);
  }
  throw new Error("No job details were found on the active LinkedIn tab.");
}
