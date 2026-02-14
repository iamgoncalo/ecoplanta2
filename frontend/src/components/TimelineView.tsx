import { Calendar, Package, MapPin } from "lucide-react";
import clsx from "clsx";

interface TimelineEntry {
  id: string;
  date: string;
  destination: string;
  items: number;
  status: string;
}

interface TimelineViewProps {
  entries: TimelineEntry[];
  title?: string;
}

function statusColor(status: string): {
  dot: string;
  bg: string;
  text: string;
} {
  const s = status.toLowerCase();
  if (s.includes("delivered") || s.includes("completed"))
    return {
      dot: "bg-[#22c55e]",
      bg: "bg-emerald-50",
      text: "text-emerald-700",
    };
  if (s.includes("transit") || s.includes("progress"))
    return {
      dot: "bg-[#eab308]",
      bg: "bg-amber-50",
      text: "text-amber-700",
    };
  return {
    dot: "bg-[#2563eb]",
    bg: "bg-blue-50",
    text: "text-blue-700",
  };
}

export default function TimelineView({
  entries,
  title = "Delivery Schedule",
}: TimelineViewProps) {
  if (entries.length === 0) {
    return (
      <div className="bg-surface rounded-xl border border-border p-5 shadow-card">
        <h3 className="text-sm font-semibold text-text-heading mb-4">
          {title}
        </h3>
        <p className="text-sm text-text-tertiary text-center py-8">
          No scheduled deliveries
        </p>
      </div>
    );
  }

  return (
    <div className="bg-surface rounded-xl border border-border p-5 shadow-card">
      <h3 className="text-sm font-semibold text-text-heading mb-4">
        {title}
      </h3>
      <div className="relative">
        {/* Vertical line */}
        <div className="absolute left-[15px] top-2 bottom-2 w-px bg-border" />

        <div className="space-y-4">
          {entries.map((entry) => {
            const colors = statusColor(entry.status);
            return (
              <div key={entry.id} className="relative flex gap-4 pl-1">
                {/* Timeline dot */}
                <div
                  className={clsx(
                    "relative z-10 w-[10px] h-[10px] rounded-full mt-1.5 shrink-0 ring-2 ring-surface",
                    colors.dot,
                  )}
                />

                {/* Content card */}
                <div className="flex-1 bg-surface-secondary rounded-lg border border-border-light p-3 hover:bg-surface-tertiary transition-colors">
                  <div className="flex items-center justify-between gap-2 mb-1.5">
                    <div className="flex items-center gap-1.5">
                      <Calendar size={12} className="text-text-tertiary" />
                      <span className="text-xs font-semibold text-text-heading">
                        {entry.date}
                      </span>
                    </div>
                    <span
                      className={clsx(
                        "inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-medium",
                        colors.bg,
                        colors.text,
                      )}
                    >
                      {entry.status}
                    </span>
                  </div>
                  <div className="flex items-center gap-3 text-xs text-text-secondary">
                    <span className="flex items-center gap-1">
                      <MapPin size={11} />
                      {entry.destination}
                    </span>
                    <span className="flex items-center gap-1">
                      <Package size={11} />
                      {entry.items} items
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
