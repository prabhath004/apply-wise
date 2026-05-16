import { createRoot } from "react-dom/client";
import { useEffect, useState } from "react";

import "../styles/globals.css";
import { saveBackendSettings } from "../sidebar/lib/apiClient";
import { defaultSettings, getSettings, saveSettings } from "../sidebar/lib/storage";
import type { ExtensionSettings } from "../sidebar/lib/types";
import { SettingsPanel } from "../sidebar/components/SettingsPanel";

function OptionsApp() {
  const [settings, setSettings] = useState<ExtensionSettings>(defaultSettings);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    getSettings().then(setSettings);
  }, []);

  async function handleSave() {
    await saveSettings(settings);
    try {
      await saveBackendSettings(settings);
      setMessage("Settings saved.");
    } catch {
      setMessage("Settings saved locally. Start the backend to sync model settings.");
    }
  }

  return (
    <main className="min-h-screen bg-surface p-6 text-ink">
      <div className="mx-auto max-w-xl">
        <h1 className="mb-4 text-xl font-semibold">ApplyIntel Settings</h1>
        <SettingsPanel settings={settings} onChange={setSettings} onSave={handleSave} />
        {message && <p className="mt-3 text-sm text-muted">{message}</p>}
      </div>
    </main>
  );
}

createRoot(document.getElementById("root") as HTMLElement).render(<OptionsApp />);
