import type { CompanyInfo } from "../lib/types";

type CompanyCardProps = {
  company: CompanyInfo;
};

export function CompanyCard({ company }: CompanyCardProps) {
  return (
    <section className="rounded-lg border border-border bg-white p-4 shadow-sm">
      <div className="flex items-center justify-between gap-3">
        <h2 className="text-sm font-semibold">Company Intelligence</h2>
        <span className="rounded-full border border-border bg-surface px-2 py-1 text-xs text-muted">
          Public sources
        </span>
      </div>
      <p className="mt-2 text-sm text-ink">
        {company.summary ?? "No public company summary was available from the captured job URL."}
      </p>
      <div className="mt-3 space-y-1 text-xs text-muted">
        {company.website && (
          <a className="block text-primary hover:underline" href={company.website} target="_blank" rel="noreferrer">
            Company website
          </a>
        )}
        {company.careers_url && (
          <a className="block text-primary hover:underline" href={company.careers_url} target="_blank" rel="noreferrer">
            Careers page
          </a>
        )}
        {company.h1b_data_url && (
          <a className="block text-primary hover:underline" href={company.h1b_data_url} target="_blank" rel="noreferrer">
            H1BData employer search
          </a>
        )}
        {company.h1b_summary && <p>{company.h1b_summary}</p>}
        {company.public_emails.length > 0 && (
          <p>Public company emails found: {company.public_emails.slice(0, 3).join(", ")}</p>
        )}
        {company.email_pattern && company.email_domain && (
          <p>
            Email pattern evidence: {company.email_pattern}@{company.email_domain}
            {company.email_pattern_confidence ? ` (${company.email_pattern_confidence}% confidence)` : ""}
          </p>
        )}
        {company.email_pattern_reason && <p>{company.email_pattern_reason}</p>}
        {company.notes.map((note) => (
          <p key={note}>{note}</p>
        ))}
      </div>
    </section>
  );
}
