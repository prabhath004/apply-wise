import { useCallback, useEffect, useState } from "react";

import { checkHealth } from "../lib/apiClient";
import { defaultSettings, getSettings, saveSettings as persistSettings } from "../lib/storage";
import type { ExtensionSettings } from "../lib/types";

export function useSettings() {
  const [settings, setSettings] = useState<ExtensionSettings>(defaultSettings);
  const [isReady, setIsReady] = useState(false);
  const [isBackendOnline, setIsBackendOnline] = useState(false);

  useEffect(() => {
    let mounted = true;
    getSettings().then(async (saved) => {
      if (!mounted) return;
      setSettings(saved);
      setIsBackendOnline(await checkHealth(saved));
      setIsReady(true);
    });
    return () => {
      mounted = false;
    };
  }, []);

  const saveSettings = useCallback(async (next: ExtensionSettings) => {
    await persistSettings(next);
    setSettings(next);
    setIsBackendOnline(await checkHealth(next));
  }, []);

  return { settings, setSettings, saveSettings, isReady, isBackendOnline };
}
