import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar.tsx";
import ConnectivitySentinel from "./ConnectivitySentinel.tsx";

export default function Layout() {
  return (
    <div className="flex h-screen overflow-hidden bg-surface-secondary">
      <Sidebar />

      <div className="flex flex-col flex-1 min-w-0">
        {/* Top bar */}
        <header className="h-14 bg-surface border-b border-border flex items-center justify-between px-6 flex-shrink-0">
          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold text-text-heading">
              EcoContainer
            </span>
            <span className="text-text-tertiary text-sm">|</span>
            <span className="text-sm text-text-secondary">
              Planta Smart Homes
            </span>
          </div>

          <div className="flex items-center gap-6">
            <ConnectivitySentinel />
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-auto p-6">
          <div className="animate-fade-in">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
