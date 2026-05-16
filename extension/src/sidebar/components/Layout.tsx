import { Settings, ShieldCheck, Wifi, WifiOff } from "lucide-react";
import type { ReactNode } from "react";

type LayoutProps = {
  isBackendOnline: boolean;
  onOpenSettings: () => void;
  children: ReactNode;
};

export function Layout({ isBackendOnline, onOpenSettings, children }: LayoutProps) {
  return (
    <main className="min-h-screen bg-[linear-gradient(180deg,#f8fafc_0%,#eef3f8_100%)] text-ink">
      <header className="sticky top-0 z-10 border-b border-border bg-white/95 px-4 py-3 backdrop-blur">
        <div className="flex items-center justify-between">
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <div className="grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-ink text-xs font-semibold text-white">
                AI
              </div>
              <div className="min-w-0">
                <h1 className="truncate text-base font-semibold tracking-normal">ApplyIntel</h1>
                <div className="mt-0.5 flex items-center gap-1.5 text-xs text-muted">
                  <ShieldCheck size={13} />
                  <span>Local-first workspace</span>
                </div>
              </div>
            </div>
            <div className="mt-3 inline-flex items-center gap-1.5 rounded-full border border-border bg-surface px-2.5 py-1 text-xs text-muted">
              {isBackendOnline ? <Wifi size={14} /> : <WifiOff size={14} />}
              <span>{isBackendOnline ? "Backend connected" : "Backend offline"}</span>
            </div>
          </div>
          <button
            className="grid h-9 w-9 shrink-0 place-items-center rounded-lg border border-border bg-white text-ink shadow-sm hover:bg-surface"
            type="button"
            aria-label="Open settings"
            onClick={onOpenSettings}
          >
            <Settings size={18} />
          </button>
        </div>
      </header>
      <div className="space-y-3.5 p-4">{children}</div>
    </main>
  );
}
