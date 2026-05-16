import { describe, expect, it } from "vitest";

import { extractLinkedInJob } from "./linkedinExtractor";

describe("extractLinkedInJob", () => {
  it("returns null when selectors are missing", () => {
    const doc = new DOMParser().parseFromString("<main></main>", "text/html");
    expect(extractLinkedInJob(doc)).toBeNull();
  });

  it("extracts a basic LinkedIn job shape", () => {
    const doc = new DOMParser().parseFromString(
      `
      <main>
        <h1>Software Engineer I</h1>
        <a href="/company/example">Example Co</a>
        <div class="jobs-description__content">Build Python and React systems.</div>
      </main>
      `,
      "text/html"
    );

    const job = extractLinkedInJob(doc);

    expect(job?.job_title).toBe("Software Engineer I");
    expect(job?.company_name).toBe("Example Co");
    expect(job?.job_description).toContain("Python");
  });

  it("extracts visible LinkedIn hiring team contacts", () => {
    const doc = new DOMParser().parseFromString(
      `
      <main>
        <h1>DevOps Engineer</h1>
        <a href="/company/mondee">Mondee</a>
        <div class="jobs-description__content">Build infrastructure systems.</div>
        <a href="/in/vikaskumar-jha">Vikaskumar Jha</a>
      </main>
      `,
      "text/html"
    );
    Object.defineProperty(doc.body, "innerText", {
      value: [
        "Meet the hiring team",
        "Vikaskumar Jha 3rd",
        "Senior Manager Talent Acquisition @ Mondee",
        "Job poster"
      ].join("\n"),
      configurable: true
    });

    const job = extractLinkedInJob(doc);

    expect(job?.page_contacts?.[0]).toMatchObject({
      name: "Vikaskumar Jha",
      title: "Senior Manager Talent Acquisition @ Mondee"
    });
  });
});
