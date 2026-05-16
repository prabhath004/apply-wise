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
});
