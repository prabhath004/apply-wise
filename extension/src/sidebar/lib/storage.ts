import type { ExtensionSettings, JobInput } from "./types";

const SETTINGS_KEY = "applyintel.settings";
const CURRENT_JOB_KEY = "applyintel.currentJob";
const RESUME_ID_KEY = "applyintel.resumeId";

export const defaultSettings: ExtensionSettings = {
  backendUrl: "http://localhost:8000",
  openaiApiKey: "",
  openaiModel: "gpt-4.1-mini",
  embeddingModel: "text-embedding-3-small"
};

type StorageShape = Record<string, unknown>;

function hasChromeStorage(): boolean {
  return Boolean(globalThis.chrome?.storage?.local);
}

async function getValues(keys: string[]): Promise<StorageShape> {
  if (hasChromeStorage()) {
    return chrome.storage.local.get(keys);
  }
  const result: StorageShape = {};
  for (const key of keys) {
    const value = globalThis.localStorage?.getItem(key);
    result[key] = value ? JSON.parse(value) : undefined;
  }
  return result;
}

async function setValues(values: StorageShape): Promise<void> {
  if (hasChromeStorage()) {
    await chrome.storage.local.set(values);
    return;
  }
  for (const [key, value] of Object.entries(values)) {
    globalThis.localStorage?.setItem(key, JSON.stringify(value));
  }
}

export async function getSettings(): Promise<ExtensionSettings> {
  const values = await getValues([SETTINGS_KEY]);
  return { ...defaultSettings, ...(values[SETTINGS_KEY] as Partial<ExtensionSettings> | undefined) };
}

export async function saveSettings(settings: ExtensionSettings): Promise<void> {
  await setValues({ [SETTINGS_KEY]: settings });
}

export async function getCurrentJob(): Promise<JobInput | null> {
  const values = await getValues([CURRENT_JOB_KEY]);
  return (values[CURRENT_JOB_KEY] as JobInput | undefined) ?? null;
}

export async function saveCurrentJob(job: JobInput): Promise<void> {
  await setValues({ [CURRENT_JOB_KEY]: job });
}

export async function getResumeId(): Promise<string | null> {
  const values = await getValues([RESUME_ID_KEY]);
  return (values[RESUME_ID_KEY] as string | undefined) ?? null;
}

export async function saveResumeId(resumeId: string): Promise<void> {
  await setValues({ [RESUME_ID_KEY]: resumeId });
}
