import { CheckCircle2, FileUp, Upload } from "lucide-react";

type ResumeStatusProps = {
  resumeId: string | null;
  status: "idle" | "loading" | "success" | "error";
  onUpload: (file: File) => void;
};

export function ResumeStatus({ resumeId, status, onUpload }: ResumeStatusProps) {
  return (
    <section className="rounded-lg border border-border bg-white p-4 shadow-sm">
      <div className="flex items-center justify-between gap-3">
        <div className="flex min-w-0 items-center gap-3">
          <div className="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-surface text-muted">
            {resumeId ? <CheckCircle2 size={17} /> : <FileUp size={17} />}
          </div>
          <div className="min-w-0">
            <h2 className="text-sm font-semibold">Resume</h2>
            <p className="mt-1 truncate text-xs text-muted">
              {resumeId ? "Ready for analysis" : "PDF or TXT required"}
            </p>
          </div>
        </div>
        <label className="inline-flex cursor-pointer items-center gap-2 rounded-lg border border-border bg-white px-3 py-2 text-xs font-semibold shadow-sm hover:bg-surface">
          <Upload size={14} />
          {status === "loading" ? "Uploading" : "Upload"}
          <input
            className="sr-only"
            type="file"
            accept=".pdf,.txt,application/pdf,text/plain"
            onChange={(event) => {
              const file = event.target.files?.[0];
              if (file) onUpload(file);
            }}
          />
        </label>
      </div>
    </section>
  );
}
