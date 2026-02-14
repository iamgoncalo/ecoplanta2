import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import type { Patent, PatentDetail } from "@/api/client.ts";
import { fetchPatentDetail } from "@/api/client.ts";
import StatusBadge from "@/components/StatusBadge.tsx";
import { FileText, ChevronDown, ChevronUp, Calendar, Lightbulb, FlaskConical } from "lucide-react";
import clsx from "clsx";

interface PatentCardProps {
  patent: Patent;
}

function statusVariant(
  status: string,
): "success" | "warning" | "info" | "neutral" {
  const s = status.toLowerCase();
  if (s === "granted") return "success";
  if (s === "pending") return "warning";
  if (s === "filed") return "info";
  return "neutral";
}

export default function PatentCard({ patent }: PatentCardProps) {
  const [expanded, setExpanded] = useState(false);

  const { data: detail } = useQuery<PatentDetail>({
    queryKey: ["patent-detail", patent.id],
    queryFn: () => fetchPatentDetail(patent.id),
    enabled: expanded,
  });

  const resolved: PatentDetail = detail ?? patent;

  return (
    <div
      className={clsx(
        "bg-surface rounded-xl border border-border shadow-card hover:shadow-elevated transition-all",
        expanded && "ring-1 ring-eco-200",
      )}
    >
      <button
        onClick={() => setExpanded((v) => !v)}
        className="w-full text-left p-5"
      >
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-lg bg-blue-50 flex items-center justify-center flex-shrink-0 mt-0.5">
              <FileText size={14} className="text-blue-600" />
            </div>
            <div>
              <h4 className="text-sm font-semibold text-text-heading">
                {patent.title}
              </h4>
              <div className="flex items-center gap-2 mt-1">
                <StatusBadge
                  label={patent.status}
                  variant={statusVariant(patent.status)}
                />
                <span className="flex items-center gap-1 text-xs text-text-tertiary">
                  <Calendar size={10} />
                  {patent.filing_date}
                </span>
              </div>
            </div>
          </div>
          <span className="text-text-tertiary mt-1">
            {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </span>
        </div>
      </button>

      {expanded && (
        <div className="px-5 pb-5 pt-0 space-y-3 border-t border-border-light ml-11">
          <p className="text-xs text-text-secondary mt-3">
            {patent.description}
          </p>

          {resolved.claims_summary && (
            <div>
              <h5 className="flex items-center gap-1.5 text-xs font-semibold text-text-heading mb-1">
                <Lightbulb size={12} className="text-amber-500" />
                Claims Summary
              </h5>
              <p className="text-xs text-text-secondary">
                {resolved.claims_summary}
              </p>
            </div>
          )}

          {resolved.experiment_results && (
            <div>
              <h5 className="flex items-center gap-1.5 text-xs font-semibold text-text-heading mb-1">
                <FlaskConical size={12} className="text-violet-500" />
                Experiment Results
              </h5>
              <p className="text-xs text-text-secondary">
                {resolved.experiment_results}
              </p>
            </div>
          )}

          {resolved.novelty_notes && (
            <div className="bg-amber-50 rounded-lg p-3">
              <h5 className="text-xs font-semibold text-amber-800 mb-1">
                Novelty Notes
              </h5>
              <p className="text-xs text-amber-700">
                {resolved.novelty_notes}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
