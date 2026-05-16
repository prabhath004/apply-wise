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

function cleanContactName(value: string): string {
  return clean(value)
    .replace(/\s+[·•]\s+\d+(st|nd|rd|th)?$/i, "")
    .replace(/\s+\d+(st|nd|rd|th)?$/i, "")
    .replace(/\s+View profile.*$/i, "")
    .trim();
}

function isLikelyName(value: string): boolean {
  const cleaned = cleanContactName(value);
  if (!cleaned || cleaned.length > 80 || cleaned.includes("@")) return false;
  const words = cleaned.split(/\s+/);
  return words.length >= 2 && words.length <= 5 && words.every((word) => /^[A-Z][A-Za-z'.-]+$/.test(word));
}

function isRecruitingTitle(value: string): boolean {
  return /recruit|talent acquisition|sourcer|hiring manager|engineering manager|job poster|people partner/i.test(value);
}

function contactNameNear(lines: string[], index: number): string | null {
  for (let offset = 1; offset <= 4; offset += 1) {
    const name = cleanContactName(lines[index - offset] ?? "");
    if (isLikelyName(name)) return name;
  }
  return null;
}

function titleNear(lines: string[], index: number): string {
  const candidates = [lines[index], lines[index - 1], lines[index + 1]].map((line) => clean(line ?? ""));
  return (
    candidates.find((candidate) => candidate && isRecruitingTitle(candidate) && !isLikelyName(candidate)) ??
    "Recruiting contact"
  );
}

function profileUrlForName(documentRef: Document, name: string): string | null {
  const anchors = Array.from(documentRef.querySelectorAll("a[href*='/in/']"));
  const normalized = name.toLowerCase();
  for (const anchor of anchors) {
    const text = clean(anchor.textContent).toLowerCase();
    if (text.includes(normalized)) {
      return new URL(anchor.getAttribute("href") ?? "", window.location.origin).toString();
    }
  }
  return null;
}

function extractVisibleContacts(documentRef: Document): JobInput["page_contacts"] {
  const lines = Array.from(new Set((documentRef.body?.innerText ?? "").split("\n").map(clean).filter(Boolean)));
  const contacts: NonNullable<JobInput["page_contacts"]> = [];
  const seen = new Set<string>();

  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index];
    if (!isRecruitingTitle(line)) continue;

    const name = contactNameNear(lines, index);
    if (!name || seen.has(name.toLowerCase())) continue;

    contacts.push({
      name,
      title: titleNear(lines, index),
      profile_url: profileUrlForName(documentRef, name),
      email: null,
      email_type: null,
      confidence: 80,
      confidence_reason: "Visible on the LinkedIn job page as a hiring team or recruiting contact.",
      sources: [{ title: "LinkedIn job page", url: window.location.href }]
    });
    seen.add(name.toLowerCase());
  }

  return contacts;
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
    job_description: description,
    page_contacts: extractVisibleContacts(documentRef)
  };
}

async function captureJobFromShortcut() {
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

  window.addEventListener(
    "keydown",
    (event) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "i") {
        event.preventDefault();
        event.stopPropagation();
        void captureJobFromShortcut();
      }
    },
    true
  );
}
