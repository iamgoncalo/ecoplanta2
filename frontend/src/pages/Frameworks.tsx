import { useQuery } from "@tanstack/react-query";
import { fetchFrameworks } from "@/api/client.ts";
import type { Framework, Material, Patent } from "@/api/client.ts";
import DataTable from "@/components/DataTable.tsx";
import type { Column } from "@/components/DataTable.tsx";
import StatusBadge from "@/components/StatusBadge.tsx";
import LoadingState from "@/components/LoadingState.tsx";
import ErrorState from "@/components/ErrorState.tsx";
import { Star, Sparkles, FileText } from "lucide-react";
import clsx from "clsx";

function RatingBar({ value, max = 10 }: { value: number; max?: number }) {
  const pct = (value / max) * 100;
  return (
    <div className="flex items-center gap-2">
      <div className="w-20 h-1.5 bg-surface-tertiary rounded-full overflow-hidden">
        <div
          className={clsx(
            "h-full rounded-full",
            pct >= 80 ? "bg-success" : pct >= 50 ? "bg-eco-500" : "bg-warning",
          )}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-xs text-text-secondary font-medium">
        {value}/{max}
      </span>
    </div>
  );
}

const materialColumns: Column<Material>[] = [
  { key: "name", header: "Material" },
  { key: "category", header: "Category" },
  {
    key: "grade",
    header: "Grade",
    render: (row) => <StatusBadge label={row.grade} />,
  },
];

const patentColumns: Column<Patent>[] = [
  { key: "title", header: "Title" },
  { key: "filing_date", header: "Filed" },
  {
    key: "status",
    header: "Status",
    render: (row) => <StatusBadge label={row.status} />,
  },
];

export default function Frameworks() {
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["frameworks"],
    queryFn: fetchFrameworks,
  });

  if (isLoading) return <LoadingState />;
  if (isError)
    return (
      <ErrorState
        message="Failed to load Frameworks data."
        onRetry={() => refetch()}
      />
    );
  if (!data) return null;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-text-heading">Frameworks</h1>
        <p className="text-sm text-text-secondary mt-0.5">
          Structural systems, materials library, and intellectual property
        </p>
      </div>

      {/* Frameworks Grid */}
      <div>
        <h2 className="text-sm font-semibold text-text-heading mb-3 flex items-center gap-2">
          <Star size={14} className="text-eco-600" />
          Structural Frameworks
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {data.frameworks.map((fw: Framework) => (
            <div
              key={fw.id}
              className="bg-surface rounded-xl border border-border p-5 shadow-card hover:shadow-elevated transition-shadow"
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="text-sm font-semibold text-text-heading">
                    {fw.name}
                  </h3>
                  <span className="text-xs text-text-tertiary">{fw.type}</span>
                </div>
                {fw.smart_enabled && (
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-semibold bg-violet-50 text-violet-700 ring-1 ring-inset ring-violet-600/10">
                    <Sparkles size={10} />
                    Smart
                  </span>
                )}
              </div>
              <p className="text-xs text-text-secondary mb-3 line-clamp-2">
                {fw.description}
              </p>
              <div className="flex items-center justify-between">
                <span className="text-xs text-text-secondary">
                  Material: {fw.material}
                </span>
                <RatingBar value={fw.structural_rating} />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Materials Library */}
      <div>
        <h2 className="text-sm font-semibold text-text-heading mb-3 flex items-center gap-2">
          <Star size={14} className="text-eco-600" />
          Materials Library
        </h2>
        <p className="text-xs text-text-secondary mb-3">
          High-quality materials only. Premium structural materials for
          sustainable container and modular construction.
        </p>
        <DataTable
          columns={materialColumns}
          data={data.materials}
          keyExtractor={(row) => row.id}
          emptyMessage="No materials in library"
        />
      </div>

      {/* Patents */}
      <div>
        <h2 className="text-sm font-semibold text-text-heading mb-3 flex items-center gap-2">
          <FileText size={14} className="text-eco-600" />
          Patents
        </h2>
        <DataTable
          columns={patentColumns}
          data={data.patents}
          keyExtractor={(row) => row.id}
          emptyMessage="No patents filed"
        />
      </div>
    </div>
  );
}
