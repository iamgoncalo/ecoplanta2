interface LoadingStateProps {
  rows?: number;
  variant?: "table" | "cards" | "page";
}

function SkeletonRow() {
  return (
    <div className="flex items-center gap-4 px-4 py-3">
      <div className="h-4 w-24 rounded animate-shimmer" />
      <div className="h-4 w-32 rounded animate-shimmer" />
      <div className="h-4 w-20 rounded animate-shimmer" />
      <div className="h-4 w-16 rounded animate-shimmer" />
    </div>
  );
}

function SkeletonCard() {
  return (
    <div className="bg-surface rounded-xl border border-border p-5">
      <div className="h-3 w-20 rounded animate-shimmer mb-3" />
      <div className="h-7 w-24 rounded animate-shimmer mb-2" />
      <div className="h-3 w-16 rounded animate-shimmer" />
    </div>
  );
}

export default function LoadingState({
  rows = 5,
  variant = "page",
}: LoadingStateProps) {
  if (variant === "cards") {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {Array.from({ length: rows }).map((_, i) => (
          <SkeletonCard key={i} />
        ))}
      </div>
    );
  }

  if (variant === "table") {
    return (
      <div className="bg-surface rounded-lg border border-border overflow-hidden">
        <div className="border-b border-border bg-surface-secondary px-4 py-3">
          <div className="flex gap-4">
            <div className="h-3 w-16 rounded animate-shimmer" />
            <div className="h-3 w-20 rounded animate-shimmer" />
            <div className="h-3 w-12 rounded animate-shimmer" />
            <div className="h-3 w-16 rounded animate-shimmer" />
          </div>
        </div>
        {Array.from({ length: rows }).map((_, i) => (
          <SkeletonRow key={i} />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <SkeletonCard key={i} />
        ))}
      </div>
      <div className="bg-surface rounded-lg border border-border overflow-hidden">
        <div className="border-b border-border bg-surface-secondary px-4 py-3">
          <div className="flex gap-4">
            <div className="h-3 w-16 rounded animate-shimmer" />
            <div className="h-3 w-20 rounded animate-shimmer" />
            <div className="h-3 w-12 rounded animate-shimmer" />
          </div>
        </div>
        {Array.from({ length: rows }).map((_, i) => (
          <SkeletonRow key={i} />
        ))}
      </div>
    </div>
  );
}
