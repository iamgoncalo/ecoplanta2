import clsx from "clsx";

interface ProgressBarProps {
  value: number;
  max?: number;
  size?: "sm" | "md" | "lg";
  showLabel?: boolean;
  label?: string;
  colorMode?: "auto" | "success" | "warning" | "danger" | "info";
}

function getAutoColor(pct: number): string {
  if (pct >= 80) return "bg-[#22c55e]";
  if (pct >= 50) return "bg-[#eab308]";
  return "bg-[#ef4444]";
}

const colorMap: Record<string, string> = {
  success: "bg-[#22c55e]",
  warning: "bg-[#eab308]",
  danger: "bg-[#ef4444]",
  info: "bg-[#2563eb]",
};

const sizeMap: Record<string, string> = {
  sm: "h-1.5",
  md: "h-2.5",
  lg: "h-4",
};

export default function ProgressBar({
  value,
  max = 100,
  size = "md",
  showLabel = true,
  label,
  colorMode = "auto",
}: ProgressBarProps) {
  const pct = Math.min(100, Math.max(0, (value / max) * 100));
  const barColor =
    colorMode === "auto" ? getAutoColor(pct) : colorMap[colorMode];

  return (
    <div className="flex items-center gap-2">
      {label && (
        <span className="text-xs text-text-secondary font-medium min-w-[60px]">
          {label}
        </span>
      )}
      <div
        className={clsx(
          "flex-1 bg-surface-tertiary rounded-full overflow-hidden",
          sizeMap[size],
        )}
      >
        <div
          className={clsx("h-full rounded-full transition-all duration-500", barColor)}
          style={{ width: `${pct}%` }}
        />
      </div>
      {showLabel && (
        <span className="text-xs text-text-secondary font-medium tabular-nums min-w-[36px] text-right">
          {Math.round(pct)}%
        </span>
      )}
    </div>
  );
}
