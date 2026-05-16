import type { JobInput } from "../lib/types";

type JobSummaryCardProps = {
  job: JobInput;
  onChange: (job: JobInput) => void;
};

export function JobSummaryCard({ job, onChange }: JobSummaryCardProps) {
  function update<K extends keyof JobInput>(key: K, value: JobInput[K]) {
    onChange({ ...job, [key]: value });
  }

  return (
    <section className="rounded-lg border border-border bg-white p-4">
      <h2 className="text-sm font-semibold">Job Snapshot</h2>
      <div className="mt-3 space-y-3">
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
          Job URL
          <input
            className="mt-1 w-full rounded-lg border border-border px-3 py-2 text-sm text-ink"
            value={job.job_url ?? ""}
            onChange={(event) => update("job_url", event.target.value)}
          />
        </label>
        <label className="block text-xs font-medium text-muted">
          Description
          <textarea
            className="mt-1 min-h-40 w-full resize-y rounded-lg border border-border px-3 py-2 text-sm text-ink"
            value={job.job_description}
            onChange={(event) => update("job_description", event.target.value)}
          />
        </label>
      </div>
    </section>
  );
}
