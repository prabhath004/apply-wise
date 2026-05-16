import { afterEach, describe, expect, it, vi } from "vitest";

import { checkHealth } from "./apiClient";
import { defaultSettings } from "./storage";

describe("apiClient", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("returns false when backend is unavailable", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("offline")));

    await expect(checkHealth(defaultSettings)).resolves.toBe(false);
  });
});
