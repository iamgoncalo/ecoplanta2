import { useState, useMemo, useCallback } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchFrameworks, fetchMaterials } from "@/api/client.ts";
import type { Framework, Material, Patent, MaterialFilters } from "@/api/client.ts";
import DataTable from "@/components/DataTable.tsx";
import type { Column } from "@/components/DataTable.tsx";
import StatusBadge from "@/components/StatusBadge.tsx";
import MaterialCard from "@/components/MaterialCard.tsx";
import ComparisonTable from "@/components/ComparisonTable.tsx";
import PatentCard from "@/components/PatentCard.tsx";
import LoadingState from "@/components/LoadingState.tsx";
import ErrorState from "@/components/ErrorState.tsx";
import { Star, Sparkles, FileText, Search, X, LayoutGrid, List } from "lucide-react";
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

/* ---------- Filter chip ---------- */
function FilterChip({
  label,
  active,
  onClick,
}: {
  label: string;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={clsx(
        "inline-flex items-center gap-1 px-3 py-1.5 rounded-full text-xs font-medium transition-colors",
        active
          ? "bg-eco-600 text-white shadow-sm"
          : "bg-surface-secondary text-text-secondary hover:bg-surface-tertiary",
      )}
    >
      {label}
      {active && <X size={10} />}
    </button>
  );
}

export default function Frameworks() {
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["frameworks"],
    queryFn: fetchFrameworks,
  });

  // Materials filters
  const [searchTerm, setSearchTerm] = useState("");
  const [categoryFilter, setCategoryFilter] = useState<string | null>(null);
  const [gradeFilter, setGradeFilter] = useState<string | null>(null);
  const [smartOnly, setSmartOnly] = useState(false);
  const [selectedMaterials, setSelectedMaterials] = useState<string[]>([]);
  const [materialsView, setMaterialsView] = useState<"grid" | "table">("grid");

  // Filtered materials query
  const filters: MaterialFilters = useMemo(
    () => ({
      category: categoryFilter ?? undefined,
      grade: gradeFilter ?? undefined,
      smart_only: smartOnly || undefined,
      search: searchTerm || undefined,
    }),
    [categoryFilter, gradeFilter, smartOnly, searchTerm],
  );

  const {
    data: materialsData,
  } = useQuery({
    queryKey: ["materials-filtered", filters],
    queryFn: () => fetchMaterials(filters),
    enabled: !!data,
  });

  // Use filtered materials if available, otherwise fall back to frameworks data
  const allMaterials = materialsData?.materials ?? data?.materials ?? [];

  // Client-side filtering as fallback
  const filteredMaterials = useMemo(() => {
    let result = allMaterials;
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      result = result.filter(
        (m) =>
          m.name.toLowerCase().includes(term) ||
          m.category.toLowerCase().includes(term),
      );
    }
    if (categoryFilter) {
      result = result.filter((m) => m.category === categoryFilter);
    }
    if (gradeFilter) {
      result = result.filter((m) => m.grade === gradeFilter);
    }
    if (smartOnly) {
      result = result.filter((m) => m.is_smart);
    }
    return result;
  }, [allMaterials, searchTerm, categoryFilter, gradeFilter, smartOnly]);

  // Unique categories/grades for filter chips
  const categories = useMemo(
    () => [...new Set(allMaterials.map((m) => m.category))].sort(),
    [allMaterials],
  );
  const grades = useMemo(
    () => [...new Set(allMaterials.map((m) => m.grade))].sort(),
    [allMaterials],
  );

  // Comparison handling
  const toggleMaterialSelect = useCallback((id: string) => {
    setSelectedMaterials((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id],
    );
  }, []);

  const selectedMaterialObjects = useMemo(
    () => allMaterials.filter((m) => selectedMaterials.includes(m.id)),
    [allMaterials, selectedMaterials],
  );

  const materialColumns: Column<Material>[] = [
    { key: "name", header: "Material" },
    { key: "category", header: "Category" },
    {
      key: "grade",
      header: "Grade",
      render: (row) => <StatusBadge label={row.grade} />,
    },
    {
      key: "strength",
      header: "Strength (MPa)",
      render: (row) => (
        <span>{row.strength != null ? row.strength : "--"}</span>
      ),
    },
    {
      key: "thermal_conductivity",
      header: "Thermal Cond.",
      render: (row) => (
        <span>
          {row.thermal_conductivity != null ? row.thermal_conductivity : "--"}
        </span>
      ),
    },
    {
      key: "embodied_carbon",
      header: "Embodied CO2",
      render: (row) => (
        <span>
          {row.embodied_carbon != null ? row.embodied_carbon : "--"}
        </span>
      ),
    },
    {
      key: "is_smart",
      header: "Smart",
      render: (row) =>
        row.is_smart ? (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-semibold bg-violet-50 text-violet-700 ring-1 ring-inset ring-violet-600/10">
            <Sparkles size={10} />
            Smart
          </span>
        ) : (
          <span className="text-text-tertiary text-xs">--</span>
        ),
    },
  ];

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
          High-quality materials for sustainable container and modular
          construction. Click materials to compare.
        </p>

        {/* Search + Filter Controls */}
        <div className="space-y-3 mb-4">
          <div className="flex items-center gap-3">
            <div className="relative flex-1 max-w-sm">
              <Search
                size={14}
                className="absolute left-3 top-1/2 -translate-y-1/2 text-text-tertiary"
              />
              <input
                type="text"
                placeholder="Search materials..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-9 pr-3 py-2 text-sm bg-surface border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-eco-500/20 focus:border-eco-400 text-text-primary placeholder:text-text-tertiary transition-colors"
              />
              {searchTerm && (
                <button
                  onClick={() => setSearchTerm("")}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-text-tertiary hover:text-text-primary"
                >
                  <X size={14} />
                </button>
              )}
            </div>
            <div className="flex items-center gap-1 bg-surface-secondary rounded-lg p-0.5">
              <button
                onClick={() => setMaterialsView("grid")}
                className={clsx(
                  "p-1.5 rounded-md transition-colors",
                  materialsView === "grid"
                    ? "bg-surface shadow-sm text-text-heading"
                    : "text-text-tertiary hover:text-text-primary",
                )}
              >
                <LayoutGrid size={14} />
              </button>
              <button
                onClick={() => setMaterialsView("table")}
                className={clsx(
                  "p-1.5 rounded-md transition-colors",
                  materialsView === "table"
                    ? "bg-surface shadow-sm text-text-heading"
                    : "text-text-tertiary hover:text-text-primary",
                )}
              >
                <List size={14} />
              </button>
            </div>
          </div>

          {/* Filter Chips */}
          <div className="flex flex-wrap gap-2">
            <FilterChip
              label="Smart Only"
              active={smartOnly}
              onClick={() => setSmartOnly((v) => !v)}
            />
            {categories.map((cat) => (
              <FilterChip
                key={cat}
                label={cat}
                active={categoryFilter === cat}
                onClick={() =>
                  setCategoryFilter((v) => (v === cat ? null : cat))
                }
              />
            ))}
            {grades.map((g) => (
              <FilterChip
                key={g}
                label={g}
                active={gradeFilter === g}
                onClick={() => setGradeFilter((v) => (v === g ? null : g))}
              />
            ))}
          </div>
        </div>

        {/* Comparison Panel */}
        {selectedMaterialObjects.length >= 2 && (
          <div className="mb-4">
            <ComparisonTable
              materials={selectedMaterialObjects}
              onRemove={(id) => toggleMaterialSelect(id)}
              onClear={() => setSelectedMaterials([])}
            />
          </div>
        )}

        {selectedMaterials.length > 0 && selectedMaterials.length < 2 && (
          <div className="mb-4 bg-blue-50 text-blue-700 rounded-lg px-4 py-2.5 text-xs font-medium">
            Select at least one more material to compare ({selectedMaterials.length}/2+ selected)
          </div>
        )}

        {/* Materials Grid or Table */}
        {materialsView === "grid" ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredMaterials.length === 0 ? (
              <div className="col-span-full bg-surface rounded-xl border border-border p-12 text-center">
                <p className="text-sm text-text-tertiary">
                  No materials match your filters
                </p>
              </div>
            ) : (
              filteredMaterials.map((m) => (
                <MaterialCard
                  key={m.id}
                  material={m}
                  selected={selectedMaterials.includes(m.id)}
                  onToggleSelect={toggleMaterialSelect}
                />
              ))
            )}
          </div>
        ) : (
          <DataTable
            columns={materialColumns}
            data={filteredMaterials}
            keyExtractor={(row) => row.id}
            emptyMessage="No materials match your filters"
          />
        )}
      </div>

      {/* Patents */}
      <div>
        <h2 className="text-sm font-semibold text-text-heading mb-3 flex items-center gap-2">
          <FileText size={14} className="text-eco-600" />
          Patents
        </h2>
        <p className="text-xs text-text-secondary mb-3">
          Click any patent to expand and view claims, experiment results, and
          novelty notes.
        </p>
        {data.patents.length === 0 ? (
          <div className="bg-surface rounded-xl border border-border p-12 text-center">
            <p className="text-sm text-text-tertiary">No patents filed</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {data.patents.map((patent: Patent) => (
              <PatentCard key={patent.id} patent={patent} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
