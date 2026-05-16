import { Upload } from "lucide-react";

type ResumeStatusProps = {
  resumeId: string | null;
  status: "idle" | "loading" | "success" | "error";
  onUpload: (file: File) => void;
};

export function ResumeStatus({ resumeId, status, onUpload }: ResumeStatusProps) {
  return (
    <section className="rounded-lg border border-border bg-white p-4">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h2 className="text-sm font-semibold">Resume</h2>
          <p className="mt-1 text-xs text-muted">
            {resumeId ? "Resume uploaded" : "Upload a PDF or TXT resume"}
          </p>
        </div>
        <label className="inline-flex cursor-pointer items-center gap-2 rounded-lg border border-border bg-white px-3 py-2 text-xs font-medium hover:bg-surface">
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
