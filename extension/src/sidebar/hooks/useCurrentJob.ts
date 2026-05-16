import { useCallback, useEffect, useState } from "react";

import { syncJobFromActiveTab } from "../lib/activeTab";
import { getCurrentJob, saveCurrentJob } from "../lib/storage";
import type { JobInput } from "../lib/types";

const emptyJob: JobInput = {
  source: "manual",
  job_title: "",
  company_name: "",
  location: "",
  job_url: "",
  job_description: ""
};

function mergeJob(existing: JobInput, incoming: JobInput): JobInput {
  if (existing.job_url && incoming.job_url && existing.job_url !== incoming.job_url) {
    return {
      ...emptyJob,
      ...incoming
    };
  }

  return {
    source: incoming.source || existing.source,
    job_title: incoming.job_title || existing.job_title,
    company_name: incoming.company_name || existing.company_name,
    location: incoming.location || existing.location,
    job_url: incoming.job_url || existing.job_url,
    job_description: incoming.job_description || existing.job_description,
    employment_type: incoming.employment_type || existing.employment_type,
    seniority: incoming.seniority || existing.seniority,
    posted_date: incoming.posted_date || existing.posted_date,
    page_contacts: incoming.page_contacts?.length ? incoming.page_contacts : existing.page_contacts
  };
}

export function useCurrentJob() {
  const [job, setJob] = useState<JobInput>(emptyJob);
  const [isLoaded, setIsLoaded] = useState(false);
  const [syncStatus, setSyncStatus] = useState<"idle" | "syncing" | "success" | "error">("idle");
  const [syncError, setSyncError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    getCurrentJob().then((saved) => {
      if (!mounted) return;
      setJob(saved ?? emptyJob);
      setIsLoaded(true);
    });
    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    if (typeof chrome === "undefined" || !chrome.storage?.onChanged) return;

    function handleStorageChange(changes: Record<string, chrome.storage.StorageChange>, areaName: string) {
      if (areaName !== "local") return;
      const nextJob = changes["applyintel.currentJob"]?.newValue;
      if (!nextJob) return;
      setJob((existing) => mergeJob(existing, nextJob as JobInput));
      setSyncStatus("success");
      setSyncError(null);
    }

    chrome.storage.onChanged.addListener(handleStorageChange);
    return () => chrome.storage.onChanged.removeListener(handleStorageChange);
  }, []);

  const updateJob = useCallback(async (next: JobInput) => {
    setJob(next);
    await saveCurrentJob(next);
  }, []);

  const syncFromActiveTab = useCallback(async () => {
    setSyncStatus("syncing");
    setSyncError(null);
    try {
      const synced = await syncJobFromActiveTab();
      const merged = mergeJob(job, synced);
      setJob(merged);
      await saveCurrentJob(merged);
      setSyncStatus("success");
      return merged;
    } catch (err) {
      setSyncStatus("error");
      setSyncError(err instanceof Error ? err.message : "Could not sync job details.");
      return null;
    }
  }, [job]);

  return { job, setJob: updateJob, isLoaded, syncFromActiveTab, syncStatus, syncError };
}
