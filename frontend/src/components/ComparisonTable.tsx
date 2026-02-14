import type { Material } from "@/api/client.ts";
import { Sparkles, X } from "lucide-react";
import clsx from "clsx";

interface ComparisonTableProps {
  materials: Material[];
  onRemove: (id: string) => void;
  onClear: () => void;
}

interface ComparisonRow {
  label: string;
  key: keyof Material | string;
  unit?: string;
  format?: (val: unknown) => string;
}

const comparisonRows: ComparisonRow[] = [
  { label: "Category", key: "category" },
  { label: "Grade", key: "grade" },
  { label: "Strength", key: "strength", unit: "MPa" },
  {
    label: "Thermal Conductivity",
    key: "thermal_conductivity",
    unit: "W/mK",
  },
  {
    label: "Embodied Carbon",
    key: "embodied_carbon",
    unit: "kgCO2/kg",
  },
  {
    label: "Smart Material",
    key: "is_smart",
    format: (v) => (v ? "Yes" : "No"),
  },
];

function getMaterialField(material: Material, key: string): unknown {
  return (material as unknown as Record<string, unknown>)[key];
}

function getCellValue(material: Material, row: ComparisonRow): string {
  const val = getMaterialField(material, row.key);
  if (val == null) return "--";
  if (row.format) return row.format(val);
  if (row.unit) return `${val} ${row.unit}`;
  return String(val);
}

export default function ComparisonTable({
  materials,
  onRemove,
  onClear,
}: ComparisonTableProps) {
  if (materials.length === 0) return null;

  return (
    <div className="bg-surface rounded-xl border border-border p-5 shadow-card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-text-heading">
          Material Comparison ({materials.length} selected)
        </h3>
        <button
          onClick={onClear}
          className="text-xs text-text-tertiary hover:text-text-primary transition-colors"
        >
          Clear all
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border">
              <th className="text-left text-xs font-semibold text-text-secondary uppercase tracking-wider px-3 py-2 min-w-[140px]">
                Property
              </th>
              {materials.map((m) => (
                <th
                  key={m.id}
                  className="text-left text-xs font-semibold text-text-heading px-3 py-2 min-w-[140px]"
                >
                  <div className="flex items-center gap-2">
                    <span>{m.name}</span>
                    {m.is_smart && (
                      <Sparkles size={10} className="text-violet-500" />
                    )}
                    <button
                      onClick={() => onRemove(m.id)}
                      className="ml-auto p-0.5 rounded hover:bg-slate-100 text-text-tertiary hover:text-text-primary transition-colors"
                    >
                      <X size={12} />
                    </button>
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {comparisonRows.map((row) => {
              const values = materials.map((m) => getCellValue(m, row));
              const numericValues = materials
                .map((m) => {
                  const v = getMaterialField(m, row.key);
                  return typeof v === "number" ? v : null;
                })
                .filter((v): v is number => v !== null);
              const maxVal =
                numericValues.length > 0 ? Math.max(...numericValues) : null;
              const isCarbon = row.key === "embodied_carbon";

              return (
                <tr
                  key={row.key}
                  className="border-b border-border-light last:border-b-0"
                >
                  <td className="px-3 py-2.5 text-xs text-text-secondary font-medium">
                    {row.label}
                    {row.unit && (
                      <span className="text-text-tertiary ml-1">
                        ({row.unit})
                      </span>
                    )}
                  </td>
                  {materials.map((m, i) => {
                    const numVal = getMaterialField(m, row.key) as
                      | number
                      | undefined;
                    const isBest =
                      maxVal !== null &&
                      numVal !== undefined &&
                      (isCarbon
                        ? numVal ===
                          Math.min(
                            ...numericValues,
                          )
                        : numVal === maxVal);

                    return (
                      <td
                        key={m.id}
                        className={clsx(
                          "px-3 py-2.5 text-xs",
                          isBest
                            ? "text-emerald-700 font-semibold"
                            : "text-text-primary",
                        )}
                      >
                        {values[i]}
                      </td>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
