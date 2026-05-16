import { beforeEach, describe, expect, it } from "vitest";

import { defaultSettings, getSettings, saveSettings } from "./storage";

describe("storage", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("saves and loads settings", async () => {
    await saveSettings({ ...defaultSettings, backendUrl: "http://localhost:9000" });

    await expect(getSettings()).resolves.toMatchObject({ backendUrl: "http://localhost:9000" });
  });
});
