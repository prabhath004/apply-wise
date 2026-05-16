import { AlertTriangle, CheckCircle2, Play, Sparkles } from "lucide-react";
import { createRoot } from "react-dom/client";
import { useEffect, useState } from "react";

import "../styles/globals.css";
import { CompanyCard } from "./components/CompanyCard";
import { ContactCard } from "./components/ContactCard";
import { ErrorState } from "./components/ErrorState";
import { JobSummaryCard } from "./components/JobSummaryCard";
import { Layout } from "./components/Layout";
import { LoadingState } from "./components/LoadingState";
import { OutreachPanel } from "./components/OutreachPanel";
import { ResumeStatus } from "./components/ResumeStatus";
import { ScoreCard } from "./components/ScoreCard";
import { SettingsPanel } from "./components/SettingsPanel";
import { useAnalysis } from "./hooks/useAnalysis";
import { useCurrentJob } from "./hooks/useCurrentJob";
import { useSettings } from "./hooks/useSettings";
import { saveBackendSettings } from "./lib/apiClient";
import { joinList } from "./lib/formatters";

function SidebarApp() {
  const [showSettings, setShowSettings] = useState(false);
  const { settings, setSettings, saveSettings, isReady, isBackendOnline } = useSettings();
  const { job, setJob, isLoaded, syncFromActiveTab, syncStatus, syncError } = useCurrentJob();
  const analysisState = useAnalysis(settings);
  const [settingsMessage, setSettingsMessage] = useState<string | null>(null);

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "i") {
        event.preventDefault();
        void syncFromActiveTab();
      }
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [syncFromActiveTab]);

  async function handleSaveSettings() {
    await saveSettings(settings);
    try {
      await saveBackendSettings(settings);
      setSettingsMessage("Settings saved.");
    } catch {
      setSettingsMessage("Settings saved locally. Backend settings were not updated.");
    }
  }

  const canAnalyze = Boolean(job.job_title && job.company_name && job.job_description && analysisState.resumeId);

  return (
    <Layout isBackendOnline={isBackendOnline} onOpenSettings={() => setShowSettings((value) => !value)}>
      {!isReady || !isLoaded ? <LoadingState label="Loading local settings..." /> : null}
      {showSettings && (
        <>
          <SettingsPanel settings={settings} onChange={setSettings} onSave={handleSaveSettings} />
          {settingsMessage && <div className="text-xs text-muted">{settingsMessage}</div>}
        </>
      )}
      {analysisState.error && <ErrorState message={analysisState.error} />}
      <ResumeStatus
        resumeId={analysisState.resumeId}
        status={analysisState.resumeStatus}
        onUpload={analysisState.upload}
      />
      <JobSummaryCard
        job={job}
        onChange={setJob}
        onSync={syncFromActiveTab}
        syncStatus={syncStatus}
        syncError={syncError}
      />
      <section className="rounded-lg border border-border bg-white p-3 shadow-sm">
        <button
          className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-primary px-3 py-2.5 text-sm font-semibold text-white shadow-sm disabled:opacity-60"
          type="button"
          disabled={!canAnalyze || analysisState.analysisStatus === "loading"}
          onClick={() => analysisState.runAnalysis(job)}
        >
          {analysisState.analysisStatus === "loading" ? <Sparkles size={15} /> : <Play size={15} />}
          {analysisState.analysisStatus === "loading" ? "Analyzing with OpenAI..." : "Analyze Job"}
        </button>
        {!analysisState.resumeId && <p className="mt-2 text-xs text-muted">Upload a resume before running analysis.</p>}
      </section>
      {analysisState.analysis && (
        <>
          <ScoreCard score={analysisState.analysis.fit_score} />
          <section className="rounded-lg border border-border bg-white p-4 shadow-sm">
            <div className="flex items-center justify-between gap-3">
              <h2 className="text-sm font-semibold">Fit Rationale</h2>
              <span className="rounded-full border border-blue-100 bg-blue-50 px-2 py-1 text-xs font-medium text-primary">
                OpenAI scored
              </span>
            </div>
            <div className="mt-3 grid gap-2 text-sm">
              <div className="rounded-lg border border-border bg-surface p-3">
                <p className="text-xs font-medium text-muted">Matching skills</p>
                <p className="mt-1 text-ink">
                  {joinList(analysisState.analysis.fit_score.matching_skills, "No direct skill matches found.")}
                </p>
              </div>
              <div className="rounded-lg border border-border bg-surface p-3">
                <p className="text-xs font-medium text-muted">Missing skills</p>
                <p className="mt-1 text-ink">
                  {joinList(analysisState.analysis.fit_score.missing_skills, "No missing required skills found.")}
                </p>
              </div>
              {analysisState.analysis.fit_score.strengths.map((item) => (
                <div key={item} className="flex gap-2 rounded-lg border border-emerald-100 bg-emerald-50 p-3 text-emerald-900">
                  <CheckCircle2 size={15} className="mt-0.5 shrink-0" />
                  <p>{item}</p>
                </div>
              ))}
              {analysisState.analysis.fit_score.risks.map((item) => (
                <div key={item} className="flex gap-2 rounded-lg border border-amber-100 bg-amber-50 p-3 text-amber-900">
                  <AlertTriangle size={15} className="mt-0.5 shrink-0" />
                  <p>{item}</p>
                </div>
              ))}
            </div>
          </section>
          <CompanyCard company={analysisState.analysis.company} />
          <section className="space-y-2">
            <h2 className="px-1 text-sm font-semibold">Contacts</h2>
            {analysisState.analysis.contacts.length ? (
              analysisState.analysis.contacts.map((contact) => <ContactCard key={contact.id ?? contact.name} contact={contact} />)
            ) : (
              <div className="rounded-lg border border-border bg-white p-4 text-sm text-muted">
                No contacts found from available public sources.
              </div>
            )}
          </section>
          <OutreachPanel
            outreach={analysisState.outreach}
            status={analysisState.outreachStatus}
            onGenerate={(tone) => analysisState.runOutreach(tone)}
          />
        </>
      )}
    </Layout>
  );
}

createRoot(document.getElementById("root") as HTMLElement).render(<SidebarApp />);
