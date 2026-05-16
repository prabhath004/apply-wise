import { useEffect, useState } from "react";

import { analyzeJob, generateOutreach, uploadResume } from "../lib/apiClient";
import { getResumeId, saveResumeId } from "../lib/storage";
import type { AnalyzeJobResponse, ExtensionSettings, JobInput, OutreachResponse } from "../lib/types";

type AsyncState = "idle" | "loading" | "success" | "error";

export function useAnalysis(settings: ExtensionSettings) {
  const [resumeId, setResumeId] = useState<string | null>(null);
  const [resumeStatus, setResumeStatus] = useState<AsyncState>("idle");
  const [analysisStatus, setAnalysisStatus] = useState<AsyncState>("idle");
  const [outreachStatus, setOutreachStatus] = useState<AsyncState>("idle");
  const [analysis, setAnalysis] = useState<AnalyzeJobResponse | null>(null);
  const [outreach, setOutreach] = useState<OutreachResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    getResumeId().then((saved) => {
      if (mounted) setResumeId(saved);
    });
    return () => {
      mounted = false;
    };
  }, []);

  async function upload(file: File) {
    setResumeStatus("loading");
    setError(null);
    try {
      const response = await uploadResume(settings, file);
      setResumeId(response.resume_id);
      await saveResumeId(response.resume_id);
      setResumeStatus("success");
    } catch (err) {
      setResumeStatus("error");
      setError(err instanceof Error ? err.message : "Could not upload resume.");
    }
  }

  async function runAnalysis(job: JobInput) {
    if (!resumeId) {
      setError("Upload a resume before analyzing a job.");
      return;
    }
    setAnalysisStatus("loading");
    setError(null);
    try {
      const response = await analyzeJob(settings, resumeId, job);
      setAnalysis(response);
      setAnalysisStatus("success");
    } catch (err) {
      setAnalysisStatus("error");
      setError(err instanceof Error ? err.message : "Could not analyze this job.");
    }
  }

  async function runOutreach(tone: "concise" | "friendly" | "formal", contactId: string | null = null) {
    if (!analysis) {
      setError("Analyze a job before generating outreach.");
      return;
    }
    setOutreachStatus("loading");
    setError(null);
    try {
      const response = await generateOutreach(settings, analysis.analysis_id, contactId, tone);
      setOutreach(response);
      setOutreachStatus("success");
    } catch (err) {
      setOutreachStatus("error");
      setError(err instanceof Error ? err.message : "Could not generate outreach.");
    }
  }

  return {
    resumeId,
    resumeStatus,
    analysisStatus,
    outreachStatus,
    analysis,
    outreach,
    error,
    upload,
    runAnalysis,
    runOutreach
  };
}
