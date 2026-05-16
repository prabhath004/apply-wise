import { Save } from "lucide-react";

import type { ExtensionSettings } from "../lib/types";

type SettingsPanelProps = {
  settings: ExtensionSettings;
  onChange: (settings: ExtensionSettings) => void;
  onSave: () => void;
};

export function SettingsPanel({ settings, onChange, onSave }: SettingsPanelProps) {
  function update<K extends keyof ExtensionSettings>(key: K, value: ExtensionSettings[K]) {
    onChange({ ...settings, [key]: value });
  }

  return (
    <section className="rounded-lg border border-border bg-white p-4">
      <h2 className="text-sm font-semibold">Settings</h2>
      <div className="mt-3 space-y-3">
        <label className="block text-xs font-medium text-muted">
          Backend URL
          <input
            className="mt-1 w-full rounded-lg border border-border px-3 py-2 text-sm text-ink"
            value={settings.backendUrl}
            onChange={(event) => update("backendUrl", event.target.value)}
          />
        </label>
        <label className="block text-xs font-medium text-muted">
          OpenAI API key
          <input
            className="mt-1 w-full rounded-lg border border-border px-3 py-2 text-sm text-ink"
            type="password"
            value={settings.openaiApiKey}
            onChange={(event) => update("openaiApiKey", event.target.value)}
          />
        </label>
        <label className="block text-xs font-medium text-muted">
          Analysis model
          <input
            className="mt-1 w-full rounded-lg border border-border px-3 py-2 text-sm text-ink"
            value={settings.openaiModel}
            onChange={(event) => update("openaiModel", event.target.value)}
          />
        </label>
        <button
          className="inline-flex items-center gap-2 rounded-lg bg-primary px-3 py-2 text-sm font-medium text-white"
          type="button"
          onClick={onSave}
        >
          <Save size={14} />
          Save
        </button>
      </div>
    </section>
  );
}
