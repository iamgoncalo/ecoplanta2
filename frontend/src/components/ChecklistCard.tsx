import { useState } from "react";
import { ChevronDown, ChevronRight, CheckCircle2, Circle } from "lucide-react";
import clsx from "clsx";
import ProgressBar from "@/components/ProgressBar.tsx";

interface ChecklistItem {
  id: string;
  label: string;
  completed: boolean;
}

interface ChecklistCardProps {
  title: string;
  subtitle?: string;
  status?: string;
  items: ChecklistItem[];
  progress: number;
  defaultExpanded?: boolean;
}

export default function ChecklistCard({
  title,
  subtitle,
  status,
  items,
  progress,
  defaultExpanded = false,
}: ChecklistCardProps) {
  const [expanded, setExpanded] = useState(defaultExpanded);

  return (
    <div className="bg-surface rounded-xl border border-border shadow-card overflow-hidden transition-shadow hover:shadow-elevated">
      <button
        type="button"
        onClick={() => setExpanded((p) => !p)}
        className="w-full flex items-center gap-3 px-5 py-4 text-left hover:bg-surface-secondary transition-colors"
      >
        <span className="text-text-tertiary">
          {expanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
        </span>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h4 className="text-sm font-semibold text-text-heading truncate">
              {title}
            </h4>
            {status && (
              <span
                className={clsx(
                  "inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-medium ring-1 ring-inset",
                  status === "completed"
                    ? "bg-emerald-50 text-emerald-700 ring-emerald-600/10"
                    : status === "in_progress"
                      ? "bg-amber-50 text-amber-700 ring-amber-600/10"
                      : "bg-blue-50 text-blue-700 ring-blue-600/10",
                )}
              >
                {status.replace(/_/g, " ")}
              </span>
            )}
          </div>
          {subtitle && (
            <p className="text-xs text-text-secondary mt-0.5 truncate">
              {subtitle}
            </p>
          )}
        </div>
        <div className="w-24 shrink-0">
          <ProgressBar value={progress} size="sm" />
        </div>
      </button>

      {expanded && (
        <div className="px-5 pb-4 border-t border-border-light">
          <ul className="space-y-2 mt-3">
            {items.map((item) => (
              <li key={item.id} className="flex items-center gap-2.5">
                {item.completed ? (
                  <CheckCircle2
                    size={16}
                    className="text-[#22c55e] shrink-0"
                  />
                ) : (
                  <Circle size={16} className="text-text-tertiary shrink-0" />
                )}
                <span
                  className={clsx(
                    "text-sm",
                    item.completed
                      ? "text-text-secondary line-through"
                      : "text-text-primary",
                  )}
                >
                  {item.label}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
