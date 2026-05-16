import { Play } from "lucide-react";
import { createRoot } from "react-dom/client";
import { useState } from "react";

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
  const { job, setJob, isLoaded } = useCurrentJob();
  const analysisState = useAnalysis(settings);
  const [settingsMessage, setSettingsMessage] = useState<string | null>(null);

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
      <JobSummaryCard job={job} onChange={setJob} />
      <button
        className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-primary px-3 py-2.5 text-sm font-semibold text-white disabled:opacity-60"
        type="button"
        disabled={!canAnalyze || analysisState.analysisStatus === "loading"}
        onClick={() => analysisState.runAnalysis(job)}
      >
        <Play size={15} />
        {analysisState.analysisStatus === "loading" ? "Analyzing..." : "Analyze Job"}
      </button>
      {!analysisState.resumeId && <p className="text-xs text-muted">Upload a resume before running analysis.</p>}
      {analysisState.analysis && (
        <>
          <ScoreCard score={analysisState.analysis.fit_score} />
          <section className="rounded-lg border border-border bg-white p-4">
            <h2 className="text-sm font-semibold">Why This Score</h2>
            <div className="mt-3 space-y-3 text-sm">
              <p>
                <span className="font-medium">Matching skills: </span>
                {joinList(analysisState.analysis.fit_score.matching_skills, "No direct skill matches found.")}
              </p>
              <p>
                <span className="font-medium">Missing skills: </span>
                {joinList(analysisState.analysis.fit_score.missing_skills, "No missing required skills found.")}
              </p>
              {analysisState.analysis.fit_score.strengths.map((item) => (
                <p key={item}>{item}</p>
              ))}
              {analysisState.analysis.fit_score.risks.map((item) => (
                <p key={item} className="text-muted">
                  {item}
                </p>
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
