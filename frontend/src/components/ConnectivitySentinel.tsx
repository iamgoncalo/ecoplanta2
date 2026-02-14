import { useState } from "react";
import { useHealth } from "@/hooks/useHealth.ts";
import clsx from "clsx";

export default function ConnectivitySentinel() {
  const { data, isError, isLoading } = useHealth();
  const [showTooltip, setShowTooltip] = useState(false);

  const isHealthy = !isError && !isLoading && data?.status === "ok";

  return (
    <div
      className="relative flex items-center gap-2 cursor-default"
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
    >
      <div
        className={clsx(
          "w-2.5 h-2.5 rounded-full transition-colors duration-300",
          isHealthy && "bg-success animate-pulse-dot",
          isError && "bg-danger",
          isLoading && "bg-warning",
        )}
      />
      <span className="text-xs font-medium text-text-secondary">
        {isHealthy ? "Connected" : isError ? "Disconnected" : "Checking..."}
      </span>

      {showTooltip && (
        <div className="absolute top-full right-0 mt-2 px-3 py-2 bg-slate-800 text-white text-xs rounded-lg shadow-modal whitespace-nowrap z-50">
          <div className="font-medium mb-1">Connectivity Sentinel</div>
          <div>
            Status: {isHealthy ? "API Healthy" : isError ? "API Unreachable" : "Polling..."}
          </div>
          {data?.version && <div>Version: {data.version}</div>}
          <div className="absolute -top-1 right-4 w-2 h-2 bg-slate-800 rotate-45" />
        </div>
      )}
    </div>
  );
}
