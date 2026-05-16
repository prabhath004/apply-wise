import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { JobSummaryCard } from "./JobSummaryCard";
import type { JobInput } from "../lib/types";

describe("JobSummaryCard", () => {
  it("supports manual job input", () => {
    const job: JobInput = {
      source: "manual",
      job_title: "",
      company_name: "",
      job_description: "",
      job_url: "",
      location: ""
    };
    const onChange = vi.fn();

    render(<JobSummaryCard job={job} onChange={onChange} />);
    fireEvent.change(screen.getByLabelText("Job title"), { target: { value: "Backend Engineer" } });

    expect(onChange).toHaveBeenCalledWith(expect.objectContaining({ job_title: "Backend Engineer" }));
  });
});
