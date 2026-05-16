import { ExternalLink, Settings } from "lucide-react";
import { createRoot } from "react-dom/client";
import { useEffect, useState } from "react";

import "../styles/globals.css";
import { checkHealth } from "../sidebar/lib/apiClient";
import { getSettings } from "../sidebar/lib/storage";

function PopupApp() {
  const [backendOnline, setBackendOnline] = useState(false);

  useEffect(() => {
    getSettings().then(async (settings) => {
      setBackendOnline(await checkHealth(settings));
    });
  }, []);

  async function openSidePanel() {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tab?.windowId) {
      await chrome.sidePanel.open({ windowId: tab.windowId });
    }
  }

  function openOptions() {
    chrome.runtime.openOptionsPage();
  }

  return (
    <main className="w-80 bg-surface p-4 text-ink">
      <div className="rounded-lg border border-border bg-white p-4">
        <h1 className="text-base font-semibold">ApplyIntel</h1>
        <p className="mt-1 text-xs text-muted">{backendOnline ? "Backend connected" : "Backend offline"}</p>
        <div className="mt-4 grid gap-2">
          <button
            className="inline-flex items-center justify-center gap-2 rounded-lg bg-primary px-3 py-2 text-sm font-medium text-white"
            type="button"
            onClick={openSidePanel}
          >
            <ExternalLink size={15} />
            Open Sidebar
          </button>
          <button
            className="inline-flex items-center justify-center gap-2 rounded-lg border border-border bg-white px-3 py-2 text-sm font-medium"
            type="button"
            onClick={openOptions}
          >
            <Settings size={15} />
            Settings
          </button>
        </div>
      </div>
    </main>
  );
}

createRoot(document.getElementById("root") as HTMLElement).render(<PopupApp />);
