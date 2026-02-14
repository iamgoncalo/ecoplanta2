import type { MLModel } from "@/api/client.ts";
import { Brain, Calendar, Activity } from "lucide-react";
import clsx from "clsx";

interface ModelCardProps {
  model: MLModel;
}

function statusColor(status: string): {
  dot: string;
  bg: string;
  text: string;
} {
  const s = status.toLowerCase();
  if (s === "active" || s === "running" || s === "deployed")
    return {
      dot: "bg-emerald-500",
      bg: "bg-emerald-50",
      text: "text-emerald-700",
    };
  if (s === "training" || s === "pending")
    return {
      dot: "bg-amber-500",
      bg: "bg-amber-50",
      text: "text-amber-700",
    };
  if (s === "error" || s === "failed")
    return { dot: "bg-red-500", bg: "bg-red-50", text: "text-red-700" };
  return {
    dot: "bg-slate-400",
    bg: "bg-slate-50",
    text: "text-slate-600",
  };
}

export default function ModelCard({ model }: ModelCardProps) {
  const colors = statusColor(model.status);
  const metricLabel = model.metric_name ?? "Accuracy";
  const metricValue = model.metric_value ?? model.accuracy;

  return (
    <div className="bg-surface rounded-xl border border-border p-5 shadow-card hover:shadow-elevated transition-shadow">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-start gap-3">
          <div className="w-9 h-9 rounded-lg bg-violet-50 flex items-center justify-center flex-shrink-0">
            <Brain size={16} className="text-violet-600" />
          </div>
          <div>
            <h4 className="text-sm font-semibold text-text-heading">
              {model.name}
            </h4>
            <span className="text-xs text-text-tertiary">{model.type}</span>
          </div>
        </div>
        <span
          className={clsx(
            "inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md text-[10px] font-semibold ring-1 ring-inset",
            colors.bg,
            colors.text,
          )}
        >
          <span className={clsx("w-1.5 h-1.5 rounded-full", colors.dot)} />
          {model.status}
        </span>
      </div>

      {model.description && (
        <p className="text-xs text-text-secondary mb-3 line-clamp-2">
          {model.description}
        </p>
      )}

      <div className="space-y-2">
        {metricValue != null && (
          <div className="flex items-center justify-between">
            <span className="flex items-center gap-1.5 text-xs text-text-secondary">
              <Activity size={12} className="text-blue-500" />
              {metricLabel}
            </span>
            <div className="flex items-center gap-2">
              <div className="w-16 h-1.5 bg-surface-tertiary rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full bg-blue-500"
                  style={{
                    width: `${Math.min(metricValue * 100, 100)}%`,
                  }}
                />
              </div>
              <span className="text-xs font-semibold text-text-heading">
                {(metricValue * 100).toFixed(1)}%
              </span>
            </div>
          </div>
        )}

        {model.last_trained && (
          <div className="flex items-center justify-between">
            <span className="flex items-center gap-1.5 text-xs text-text-secondary">
              <Calendar size={12} className="text-slate-400" />
              Last Trained
            </span>
            <span className="text-xs text-text-primary">
              {model.last_trained}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
