import { confidenceLabel } from "../lib/formatters";
import type { ContactInfo } from "../lib/types";

type ContactCardProps = {
  contact: ContactInfo;
};

export function ContactCard({ contact }: ContactCardProps) {
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
        <p className="mt-3 break-all text-sm">
          {contact.email}{" "}
          {contact.email_type === "inferred" && <span className="text-xs text-muted">(inferred)</span>}
        </p>
      )}
      {contact.confidence_reason && <p className="mt-2 text-xs text-muted">{contact.confidence_reason}</p>}
      {contact.profile_url && (
        <a className="mt-2 block text-xs text-primary hover:underline" href={contact.profile_url} target="_blank" rel="noreferrer">
          Public profile
        </a>
      )}
    </article>
  );
}
