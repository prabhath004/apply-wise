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

  const updateJob = useCallback(async (next: JobInput) => {
    setJob(next);
    await saveCurrentJob(next);
  }, []);

  const syncFromActiveTab = useCallback(async () => {
    setSyncStatus("syncing");
    setSyncError(null);
    try {
      const synced = await syncJobFromActiveTab();
      setJob(synced);
      setSyncStatus("success");
      return synced;
    } catch (err) {
      setSyncStatus("error");
      setSyncError(err instanceof Error ? err.message : "Could not sync job details.");
      return null;
    }
  }, []);

  return { job, setJob: updateJob, isLoaded, syncFromActiveTab, syncStatus, syncError };
}
