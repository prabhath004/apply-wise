import { Copy, ExternalLink, Mail } from "lucide-react";

import { confidenceLabel } from "../lib/formatters";
import type { ContactInfo } from "../lib/types";

type ContactCardProps = {
  contact: ContactInfo;
};

export function ContactCard({ contact }: ContactCardProps) {
  const extraSources = contact.sources
    .filter((source) => source.url !== contact.profile_url && source.title !== "LinkedIn job page")
    .slice(0, 2);

  async function copyEmail() {
    if (!contact.email) return;
    await navigator.clipboard.writeText(contact.email);
  }

  return (
    <article className="rounded-lg border border-border bg-white p-3 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="text-sm font-semibold">{contact.name}</h3>
          {contact.title && <p className="mt-1 text-xs text-muted">{contact.title}</p>}
        </div>
        <span className="rounded-full border border-border px-2 py-1 text-xs text-muted">
          {confidenceLabel(contact.confidence)}
        </span>
      </div>
      {contact.email && (
        <div className="mt-3 rounded-lg border border-blue-100 bg-blue-50 p-2">
          <p className="mb-1 text-xs font-medium text-primary">
            {contact.email_type === "public" ? "Public email" : "Likely email"}
          </p>
          <div className="flex items-center gap-2">
            <Mail size={14} className="shrink-0 text-primary" />
            <a className="min-w-0 flex-1 break-all text-sm font-medium text-ink hover:underline" href={`mailto:${contact.email}`}>
              {contact.email}
            </a>
            <button
              className="rounded-md border border-blue-100 bg-white p-1.5 text-primary shadow-sm"
              type="button"
              title="Copy email"
              onClick={copyEmail}
            >
              <Copy size={13} />
            </button>
          </div>
        </div>
      )}
      {contact.confidence_reason && <p className="mt-2 text-xs text-muted">{contact.confidence_reason}</p>}
      {contact.profile_url && (
        <a
          className="mt-2 inline-flex items-center gap-1 text-xs text-primary hover:underline"
          href={contact.profile_url}
          target="_blank"
          rel="noreferrer"
        >
          {contact.email_type === "search_link" ? "Open search" : "Public profile"}
          <ExternalLink size={12} />
        </a>
      )}
      {extraSources.map((source) => (
        <a
          key={source.url}
          className="ml-3 mt-2 inline-flex items-center gap-1 text-xs text-primary hover:underline first:ml-0"
          href={source.url}
          target="_blank"
          rel="noreferrer"
        >
          {source.title}
          <ExternalLink size={12} />
        </a>
      ))}
    </article>
  );
}
