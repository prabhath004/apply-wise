import { textFromManySelectors, textFromSelectors } from "./domUtils";
import type { JobInput } from "../sidebar/lib/types";

const TITLE_SELECTORS = [
  ".job-details-jobs-unified-top-card__job-title",
  ".jobs-unified-top-card__job-title",
  ".jobs-search__job-details--container h1",
  "[data-test-job-title]",
  "h1"
];

const COMPANY_SELECTORS = [
  ".job-details-jobs-unified-top-card__company-name a",
  ".jobs-unified-top-card__company-name a",
  ".jobs-search__job-details--container a[href*='/company/']",
  "a[href*='/company/']"
];

const LOCATION_SELECTORS = [
  ".job-details-jobs-unified-top-card__primary-description-container",
  ".job-details-jobs-unified-top-card__primary-description-container span",
  ".jobs-unified-top-card__bullet",
  ".jobs-unified-top-card__workplace-type",
  ".jobs-search__job-details--container [class*='primary-description']"
];

const DESCRIPTION_SELECTORS = [
  "#job-details",
  ".jobs-description",
  ".jobs-description__container",
  ".jobs-description__content",
  ".jobs-box__html-content",
  ".jobs-description-content__text",
  "[class*='jobs-description']"
];

function clean(value: string | null): string {
  return value?.replace(/\s+/g, " ").trim() ?? "";
}

function cleanLinkedInTitle(value: string): string {
  return value
    .replace(/\s+\|\s+LinkedIn.*$/i, "")
    .replace(/\s+-\s+LinkedIn.*$/i, "")
    .replace(/\s+at\s+.+$/i, "")
    .trim();
}

function titleFromDocument(documentRef: Document): string {
  const title = cleanLinkedInTitle(documentRef.title);
  if (!title || /linkedin/i.test(title) || title.length > 120) return "";
  return title;
}

function locationFromText(value: string): string {
  const cleaned = clean(value);
  if (!cleaned) return "";
  return cleaned.split("·")[0]?.trim() ?? cleaned;
}

function bestDescription(documentRef: Document): string {
  const fromSelectors = textFromManySelectors(DESCRIPTION_SELECTORS, documentRef).trim();
  if (fromSelectors.length > 80) return fromSelectors;

  const bodyText = clean(documentRef.body?.innerText ?? "");
  const marker = bodyText.toLowerCase().indexOf("about the job");
  if (marker >= 0) {
    return bodyText.slice(marker).replace(/^about the job\s*/i, "").trim();
  }
  return fromSelectors;
}

export function extractLinkedInJob(documentRef: Document = document): JobInput | null {
  const title = clean(textFromSelectors(TITLE_SELECTORS, documentRef)) || titleFromDocument(documentRef);
  const company = clean(textFromSelectors(COMPANY_SELECTORS, documentRef));
  const description = bestDescription(documentRef);
  const location = locationFromText(textFromSelectors(LOCATION_SELECTORS, documentRef) ?? "");

  if (!title && !company && !description) {
    return null;
  }

  return {
    source: "linkedin",
    job_title: title,
    company_name: company,
    location,
    job_url: window.location.href,
    job_description: description
  };
}

async function storeExtractedJob() {
  const job = extractLinkedInJob();
  if (!job || typeof chrome === "undefined" || !chrome.storage?.local) return;
  await chrome.storage.local.set({ "applyintel.currentJob": job });
}

if (typeof chrome !== "undefined" && chrome.storage?.local) {
  chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
    if (message?.type !== "APPLYINTEL_EXTRACT_JOB") return false;
    const job = extractLinkedInJob();
    if (job) {
      void chrome.storage.local.set({ "applyintel.currentJob": job });
    }
    sendResponse({ job });
    return false;
  });

  void storeExtractedJob();

  let lastUrl = window.location.href;
  const observer = new MutationObserver(() => {
    if (window.location.href !== lastUrl) {
      lastUrl = window.location.href;
      window.setTimeout(() => void storeExtractedJob(), 800);
    }
  });

  observer.observe(document.documentElement, { childList: true, subtree: true });
}
