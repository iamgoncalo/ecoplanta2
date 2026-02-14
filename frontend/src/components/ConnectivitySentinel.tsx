import { useState } from "react";
import { useHealth } from "@/hooks/useHealth.ts";
import { isBackendOnline } from "@/api/client.ts";
import clsx from "clsx";

export default function ConnectivitySentinel() {
  const { data, isError, isLoading } = useHealth();
  const [showTooltip, setShowTooltip] = useState(false);

  const isHealthy = !isError && !isLoading && data?.status === "ok";
  const backendStatus = isBackendOnline();
  const usingFallback = backendStatus === false;

  const label = isHealthy
    ? "ONLINE"
    : usingFallback
      ? "PREVIEW"
      : isLoading
        ? "..."
        : "OFFLINE";

  return (
    <div
      className="relative flex items-center gap-2 cursor-default"
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
    >
      <div
        className={clsx(
          "flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-semibold tracking-wide uppercase transition-colors duration-300",
          isHealthy && "bg-emerald-50 text-emerald-700 border border-emerald-200",
          usingFallback && !isHealthy && "bg-amber-50 text-amber-700 border border-amber-200",
          !isHealthy && !usingFallback && !isLoading && "bg-red-50 text-red-700 border border-red-200",
          isLoading && "bg-slate-50 text-slate-500 border border-slate-200",
        )}
      >
        <div
          className={clsx(
            "w-1.5 h-1.5 rounded-full",
            isHealthy && "bg-emerald-500",
            usingFallback && !isHealthy && "bg-amber-500",
            !isHealthy && !usingFallback && !isLoading && "bg-red-500",
            isLoading && "bg-slate-400 animate-pulse",
          )}
        />
        Backend: {label}
      </div>

      {showTooltip && (
        <div className="absolute top-full right-0 mt-2 px-3 py-2 bg-slate-800 text-white text-xs rounded-lg shadow-lg whitespace-nowrap z-50">
          <div className="font-medium mb-1">Connectivity Sentinel</div>
          {isHealthy && <div>API is healthy and responding</div>}
          {usingFallback && !isHealthy && <div>Using static preview data (SEED=42)</div>}
          {!isHealthy && !usingFallback && !isLoading && <div>Backend API is unreachable</div>}
          {isLoading && <div>Checking backend connectivity...</div>}
          {data?.version && <div className="mt-1 text-slate-400">v{data.version}</div>}
          <div className="absolute -top-1 right-4 w-2 h-2 bg-slate-800 rotate-45" />
        </div>
      )}
    </div>
  );
}
