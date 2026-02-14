import { ArrowUpRight, ArrowDownRight, Minus } from "lucide-react";
import clsx from "clsx";

interface MetricCardProps {
  title: string;
  value: string | number;
  unit?: string;
  change?: number;
  trend?: string;
  icon?: React.ComponentType<{ size?: number; className?: string }>;
}

export default function MetricCard({
  title,
  value,
  unit,
  change,
  trend,
  icon: Icon,
}: MetricCardProps) {
  const isPositive = trend === "up" || (change !== undefined && change > 0);
  const isNegative = trend === "down" || (change !== undefined && change < 0);

  return (
    <div className="bg-surface rounded-xl border border-border p-5 shadow-card transition-shadow hover:shadow-elevated">
      <div className="flex items-start justify-between mb-3">
        <span className="text-xs font-semibold text-text-secondary uppercase tracking-wider">
          {title}
        </span>
        {Icon && (
          <Icon size={16} className="text-text-tertiary" />
        )}
      </div>

      <div className="flex items-baseline gap-1.5">
        <span className="text-2xl font-bold text-text-heading tracking-tight">
          {typeof value === "number" ? value.toLocaleString() : value}
        </span>
        {unit && (
          <span className="text-sm text-text-tertiary">{unit}</span>
        )}
      </div>

      {change !== undefined && (
        <div className="flex items-center gap-1 mt-2">
          {isPositive ? (
            <ArrowUpRight size={14} className="text-success" />
          ) : isNegative ? (
            <ArrowDownRight size={14} className="text-danger" />
          ) : (
            <Minus size={14} className="text-text-tertiary" />
          )}
          <span
            className={clsx(
              "text-xs font-medium",
              isPositive && "text-success",
              isNegative && "text-danger",
              !isPositive && !isNegative && "text-text-tertiary",
            )}
          >
            {Math.abs(change)}%
          </span>
          <span className="text-xs text-text-tertiary">vs last period</span>
        </div>
      )}
    </div>
  );
}
