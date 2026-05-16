import { textFromManySelectors, textFromSelectors } from "./domUtils";
import type { JobInput } from "../sidebar/lib/types";

const TITLE_SELECTORS = [
  "h1",
  ".job-details-jobs-unified-top-card__job-title",
  ".jobs-unified-top-card__job-title"
];

const COMPANY_SELECTORS = [
  ".job-details-jobs-unified-top-card__company-name a",
  ".jobs-unified-top-card__company-name a",
  "a[href*='/company/']"
];

const LOCATION_SELECTORS = [
  ".job-details-jobs-unified-top-card__primary-description-container span",
  ".jobs-unified-top-card__bullet",
  ".jobs-unified-top-card__workplace-type"
];

const DESCRIPTION_SELECTORS = [
  ".jobs-description__content",
  ".jobs-box__html-content",
  ".jobs-description-content__text",
  "[class*='jobs-description']"
];

function clean(value: string | null): string {
  return value?.replace(/\s+/g, " ").trim() ?? "";
}

export function extractLinkedInJob(documentRef: Document = document): JobInput | null {
  const title = clean(textFromSelectors(TITLE_SELECTORS, documentRef));
  const company = clean(textFromSelectors(COMPANY_SELECTORS, documentRef));
  const description = textFromManySelectors(DESCRIPTION_SELECTORS, documentRef).trim();
  const location = clean(textFromSelectors(LOCATION_SELECTORS, documentRef));

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
