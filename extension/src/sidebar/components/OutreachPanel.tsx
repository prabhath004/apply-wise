import { Copy } from "lucide-react";
import { useEffect, useState } from "react";

import type { OutreachResponse } from "../lib/types";

type OutreachPanelProps = {
  outreach: OutreachResponse | null;
  status: "idle" | "loading" | "success" | "error";
  onGenerate: (tone: "concise" | "friendly" | "formal") => void;
};

export function OutreachPanel({ outreach, status, onGenerate }: OutreachPanelProps) {
  const [tone, setTone] = useState<"concise" | "friendly" | "formal">("concise");
  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");

  useEffect(() => {
    if (!outreach) return;
    setSubject(outreach.subject ?? "");
    setBody(outreach.body);
  }, [outreach]);

  async function copy() {
    const value = [subject, body].filter(Boolean).join("\n\n");
    await navigator.clipboard.writeText(value);
  }

  return (
    <section className="rounded-lg border border-border bg-white p-4 shadow-sm">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold">Outreach</h2>
        <select
          className="rounded-lg border border-border bg-white px-2 py-1 text-xs"
          value={tone}
          onChange={(event) => setTone(event.target.value as "concise" | "friendly" | "formal")}
        >
          <option value="concise">Concise</option>
          <option value="friendly">Friendly</option>
          <option value="formal">Formal</option>
        </select>
      </div>
      <button
        className="mt-3 w-full rounded-lg bg-primary px-3 py-2 text-sm font-semibold text-white shadow-sm disabled:opacity-60"
        type="button"
        disabled={status === "loading"}
        onClick={() => onGenerate(tone)}
      >
        {status === "loading" ? "Generating..." : "Generate Message"}
      </button>
      {outreach && (
        <div className="mt-3 rounded-lg border border-border bg-surface p-3">
          <label className="block text-xs font-medium text-muted" htmlFor="outreach-subject">
            Subject
          </label>
          <input
            id="outreach-subject"
            className="mt-1 w-full rounded-lg border border-border bg-white px-3 py-2 text-sm text-ink outline-none focus:border-primary"
            value={subject}
            onChange={(event) => setSubject(event.target.value)}
          />
          <label className="mt-3 block text-xs font-medium text-muted" htmlFor="outreach-body">
            Message
          </label>
          <textarea
            id="outreach-body"
            className="mt-1 min-h-52 w-full resize-y rounded-lg border border-border bg-white px-3 py-2 text-sm leading-6 text-ink outline-none focus:border-primary"
            value={body}
            onChange={(event) => setBody(event.target.value)}
          />
          <button
            className="mt-3 inline-flex items-center gap-2 rounded-lg border border-border bg-white px-3 py-2 text-xs font-medium"
            type="button"
            disabled={!subject && !body}
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
