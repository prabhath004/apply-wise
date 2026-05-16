import { BriefcaseBusiness, CheckCircle2, ExternalLink, FileText, MapPin, Pencil, RefreshCw } from "lucide-react";
import { useState } from "react";

import type { JobInput } from "../lib/types";

type JobSummaryCardProps = {
  job: JobInput;
  onChange: (job: JobInput) => void;
  onSync: () => void;
  syncStatus: "idle" | "syncing" | "success" | "error";
  syncError: string | null;
};

function hasSnapshot(job: JobInput): boolean {
  return Boolean(job.job_title || job.company_name || job.job_description);
}

function descriptionPreview(value: string): string {
  if (!value) return "No description captured yet.";
  return value.length > 220 ? `${value.slice(0, 220).trim()}...` : value;
}

export function JobSummaryCard({ job, onChange, onSync, syncStatus, syncError }: JobSummaryCardProps) {
  const [isEditing, setIsEditing] = useState(false);

  function update<K extends keyof JobInput>(key: K, value: JobInput[K]) {
    onChange({ ...job, [key]: value });
  }

  return (
    <section className="overflow-hidden rounded-lg border border-border bg-white shadow-sm">
      <div className="border-b border-border bg-white px-4 py-3">
        <div className="flex items-center justify-between gap-3">
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-semibold">Job Snapshot</h2>
              {hasSnapshot(job) && (
                <span className="inline-flex items-center gap-1 rounded-full border border-emerald-200 bg-emerald-50 px-2 py-0.5 text-xs font-medium text-emerald-700">
                  <CheckCircle2 size={12} />
                  Synced
                </span>
              )}
            </div>
            <p className="mt-1 text-xs text-muted">Active job page</p>
          </div>
          <div className="flex shrink-0 items-center gap-2">
            <button
              className="grid h-8 w-8 place-items-center rounded-lg border border-border bg-white text-muted hover:bg-surface hover:text-ink"
              type="button"
              title="Edit fallback fields"
              aria-label="Edit fallback fields"
              onClick={() => setIsEditing((value) => !value)}
            >
              <Pencil size={14} />
            </button>
            <button
              className="inline-flex h-8 items-center gap-2 rounded-lg bg-ink px-3 text-xs font-semibold text-white disabled:opacity-60"
              type="button"
              title="Sync current tab"
              disabled={syncStatus === "syncing"}
              onClick={onSync}
            >
              <RefreshCw size={14} className={syncStatus === "syncing" ? "animate-spin" : ""} />
              Sync
            </button>
          </div>
        </div>
      </div>

      {!hasSnapshot(job) ? (
        <div className="p-4">
          <div className="rounded-lg border border-dashed border-border bg-surface p-4">
            <p className="text-sm font-medium text-ink">No active job captured</p>
            <p className="mt-1 text-xs leading-5 text-muted">Waiting for a LinkedIn job page.</p>
          </div>
        </div>
      ) : (
        <div className="space-y-3 p-4">
          <div>
            <p className="text-xs font-medium uppercase tracking-normal text-muted">Role</p>
            <h3 className="mt-1 text-lg font-semibold leading-6 text-ink">{job.job_title || "Untitled role"}</h3>
          </div>
          <div className="grid gap-2 text-sm">
            <div className="flex items-center gap-2 text-ink">
              <BriefcaseBusiness size={15} className="shrink-0 text-muted" />
              <span className="min-w-0 truncate">{job.company_name || "Company unavailable"}</span>
            </div>
            <div className="flex items-center gap-2 text-muted">
              <MapPin size={15} className="shrink-0" />
              <span className="min-w-0 truncate">{job.location || "Location unavailable"}</span>
            </div>
            {job.job_url && (
              <a
                className="flex items-center gap-2 text-primary hover:underline"
                href={job.job_url}
                target="_blank"
                rel="noreferrer"
              >
                <ExternalLink size={15} className="shrink-0" />
                <span className="min-w-0 truncate">Source page</span>
              </a>
            )}
          </div>
          <div className="rounded-lg border border-border bg-surface p-3">
            <div className="mb-2 flex items-center gap-2 text-xs font-medium text-muted">
              <FileText size={14} />
              Description
            </div>
            <p className="text-sm leading-5 text-ink">{descriptionPreview(job.job_description)}</p>
          </div>
        </div>
      )}

      {syncError && <div className="border-t border-red-100 bg-red-50 px-4 py-2 text-xs text-red-800">{syncError}</div>}

      {isEditing && (
        <div className="space-y-3 border-t border-border bg-[#fbfcfe] p-4">
          <label className="block text-xs font-medium text-muted">
            Job title
            <input
              className="mt-1 w-full rounded-lg border border-border px-3 py-2 text-sm text-ink"
              value={job.job_title}
              onChange={(event) => update("job_title", event.target.value)}
            />
          </label>
          <label className="block text-xs font-medium text-muted">
            Company
            <input
              className="mt-1 w-full rounded-lg border border-border px-3 py-2 text-sm text-ink"
              value={job.company_name}
              onChange={(event) => update("company_name", event.target.value)}
            />
          </label>
          <label className="block text-xs font-medium text-muted">
            Location
            <input
              className="mt-1 w-full rounded-lg border border-border px-3 py-2 text-sm text-ink"
              value={job.location ?? ""}
              onChange={(event) => update("location", event.target.value)}
            />
          </label>
          <label className="block text-xs font-medium text-muted">
            Description
            <textarea
              className="mt-1 min-h-36 w-full resize-y rounded-lg border border-border px-3 py-2 text-sm text-ink"
              value={job.job_description}
              onChange={(event) => update("job_description", event.target.value)}
            />
          </label>
        </div>
      )}
    </section>
  );
}
