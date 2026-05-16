import { Settings, Wifi, WifiOff } from "lucide-react";
import type { ReactNode } from "react";

type LayoutProps = {
  isBackendOnline: boolean;
  onOpenSettings: () => void;
  children: ReactNode;
};

export function Layout({ isBackendOnline, onOpenSettings, children }: LayoutProps) {
  return (
    <main className="min-h-screen bg-surface text-ink">
      <header className="sticky top-0 z-10 border-b border-border bg-white px-4 py-3">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-base font-semibold">ApplyIntel</h1>
            <div className="mt-1 flex items-center gap-1.5 text-xs text-muted">
              {isBackendOnline ? <Wifi size={14} /> : <WifiOff size={14} />}
              <span>{isBackendOnline ? "Backend connected" : "Backend offline"}</span>
            </div>
          </div>
          <button
            className="grid h-9 w-9 place-items-center rounded-lg border border-border bg-white text-ink hover:bg-surface"
            type="button"
            aria-label="Open settings"
            onClick={onOpenSettings}
          >
            <Settings size={18} />
          </button>
        </div>
      </header>
      <div className="space-y-3 p-4">{children}</div>
    </main>
  );
}
