import type { Partner } from "@/api/client.ts";
import StatusBadge from "@/components/StatusBadge.tsx";
import { Star, Clock, MapPin } from "lucide-react";
import clsx from "clsx";

interface PartnerCardProps {
  partner: Partner;
}

const regionColors: Record<string, string> = {
  Germany: "border-l-blue-500",
  Spain: "border-l-red-500",
  France: "border-l-indigo-500",
  Italy: "border-l-emerald-500",
  Poland: "border-l-rose-500",
  Netherlands: "border-l-orange-500",
  Portugal: "border-l-teal-500",
  Belgium: "border-l-amber-500",
  Austria: "border-l-cyan-500",
  Sweden: "border-l-yellow-500",
};

function getRegionColor(country?: string, region?: string): string {
  if (country && regionColors[country]) return regionColors[country];
  if (region && regionColors[region]) return regionColors[region];
  return "border-l-slate-300";
}

function RatingStars({ rating, max = 5 }: { rating: number; max?: number }) {
  return (
    <div className="flex items-center gap-0.5">
      {Array.from({ length: max }).map((_, i) => (
        <Star
          key={i}
          size={12}
          className={clsx(
            i < rating ? "text-amber-400 fill-amber-400" : "text-slate-200",
          )}
        />
      ))}
    </div>
  );
}

export default function PartnerCard({ partner }: PartnerCardProps) {
  const country = partner.country ?? partner.region;

  return (
    <div
      className={clsx(
        "bg-surface rounded-xl border border-border border-l-4 p-5 shadow-card hover:shadow-elevated transition-shadow",
        getRegionColor(partner.country, partner.region),
      )}
    >
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="text-sm font-semibold text-text-heading">
            {partner.name}
          </h3>
          <span className="flex items-center gap-1 text-xs text-text-tertiary">
            <MapPin size={10} />
            {partner.type} &middot; {country}
          </span>
        </div>
        <StatusBadge label={partner.compliance_status} />
      </div>

      <div className="space-y-2">
        {/* Capacity gauge */}
        <div className="flex items-center justify-between">
          <span className="text-xs text-text-secondary">Capacity</span>
          <div className="flex items-center gap-2">
            <div className="w-20 h-1.5 bg-surface-tertiary rounded-full overflow-hidden">
              <div
                className={clsx(
                  "h-full rounded-full",
                  partner.capacity_utilization >= 80
                    ? "bg-danger"
                    : partner.capacity_utilization >= 50
                      ? "bg-warning"
                      : "bg-success",
                )}
                style={{ width: `${partner.capacity_utilization}%` }}
              />
            </div>
            <span className="text-xs text-text-secondary font-medium w-8 text-right">
              {partner.capacity_utilization}%
            </span>
          </div>
        </div>

        {partner.capacity != null && (
          <div className="flex items-center justify-between">
            <span className="text-xs text-text-secondary">Total Capacity</span>
            <span className="text-xs font-medium text-text-primary">
              {partner.capacity.toLocaleString()} units
            </span>
          </div>
        )}

        {partner.lead_time != null && (
          <div className="flex items-center justify-between">
            <span className="flex items-center gap-1 text-xs text-text-secondary">
              <Clock size={10} />
              Lead Time
            </span>
            <span className="text-xs font-medium text-text-primary">
              {partner.lead_time} days
            </span>
          </div>
        )}

        <div className="flex items-center justify-between">
          <span className="text-xs text-text-secondary">Active Projects</span>
          <span className="text-xs font-medium text-text-primary">
            {partner.active_projects}
          </span>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-xs text-text-secondary">Rating</span>
          <RatingStars rating={partner.rating} />
        </div>
      </div>
    </div>
  );
}
