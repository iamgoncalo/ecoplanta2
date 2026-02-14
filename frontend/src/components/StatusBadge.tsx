import clsx from "clsx";

type BadgeVariant = "success" | "warning" | "danger" | "info" | "neutral";

interface StatusBadgeProps {
  label: string;
  variant?: BadgeVariant;
}

const variantClasses: Record<BadgeVariant, string> = {
  success: "bg-emerald-50 text-emerald-700 ring-emerald-600/10",
  warning: "bg-amber-50 text-amber-700 ring-amber-600/10",
  danger: "bg-red-50 text-red-700 ring-red-600/10",
  info: "bg-blue-50 text-blue-700 ring-blue-600/10",
  neutral: "bg-slate-50 text-slate-600 ring-slate-500/10",
};

export function statusToVariant(status: string): BadgeVariant {
  const s = status.toLowerCase();
  if (
    s.includes("active") ||
    s.includes("complete") ||
    s.includes("running") ||
    s.includes("healthy") ||
    s.includes("approved") ||
    s.includes("granted") ||
    s.includes("compliant") ||
    s.includes("delivered") ||
    s.includes("won")
  )
    return "success";
  if (
    s.includes("pending") ||
    s.includes("progress") ||
    s.includes("review") ||
    s.includes("transit") ||
    s.includes("negotiation") ||
    s.includes("partial")
  )
    return "warning";
  if (
    s.includes("error") ||
    s.includes("fail") ||
    s.includes("down") ||
    s.includes("rejected") ||
    s.includes("overdue") ||
    s.includes("lost") ||
    s.includes("non-compliant")
  )
    return "danger";
  if (
    s.includes("new") ||
    s.includes("qualified") ||
    s.includes("scheduled") ||
    s.includes("smart") ||
    s.includes("planned") ||
    s.includes("discovery") ||
    s.includes("proposal")
  )
    return "info";
  return "neutral";
}

export default function StatusBadge({ label, variant }: StatusBadgeProps) {
  const v = variant ?? statusToVariant(label);

  return (
    <span
      className={clsx(
        "inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium ring-1 ring-inset",
        variantClasses[v],
      )}
    >
      {label}
    </span>
  );
}
