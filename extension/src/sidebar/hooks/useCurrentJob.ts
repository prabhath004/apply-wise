import { useCallback, useEffect, useState } from "react";

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

  return { job, setJob: updateJob, isLoaded };
}
