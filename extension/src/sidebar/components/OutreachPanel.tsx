import { Copy } from "lucide-react";

import type { OutreachResponse } from "../lib/types";

type OutreachPanelProps = {
  outreach: OutreachResponse | null;
  status: "idle" | "loading" | "success" | "error";
  onGenerate: (tone: "concise" | "friendly" | "formal") => void;
};

export function OutreachPanel({ outreach, status, onGenerate }: OutreachPanelProps) {
  async function copy() {
    if (!outreach) return;
    const value = [outreach.subject, outreach.body].filter(Boolean).join("\n\n");
    await navigator.clipboard.writeText(value);
  }

  return (
    <section className="rounded-lg border border-border bg-white p-4">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold">Outreach</h2>
        <select
          className="rounded-lg border border-border bg-white px-2 py-1 text-xs"
          defaultValue="concise"
          onChange={(event) => onGenerate(event.target.value as "concise" | "friendly" | "formal")}
        >
          <option value="concise">Concise</option>
          <option value="friendly">Friendly</option>
          <option value="formal">Formal</option>
        </select>
      </div>
      <button
        className="mt-3 w-full rounded-lg bg-primary px-3 py-2 text-sm font-medium text-white disabled:opacity-60"
        type="button"
        disabled={status === "loading"}
        onClick={() => onGenerate("concise")}
      >
        {status === "loading" ? "Generating..." : "Generate Message"}
      </button>
      {outreach && (
        <div className="mt-3 rounded-lg border border-border bg-surface p-3">
          {outreach.subject && <p className="mb-2 text-sm font-medium">{outreach.subject}</p>}
          <pre className="whitespace-pre-wrap break-words text-sm font-sans text-ink">{outreach.body}</pre>
          <button
            className="mt-3 inline-flex items-center gap-2 rounded-lg border border-border bg-white px-3 py-2 text-xs font-medium"
            type="button"
            onClick={copy}
          >
            <Copy size={14} />
            Copy
          </button>
        </div>
      )}
    </section>
  );
}
