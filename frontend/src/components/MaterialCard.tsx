import type { Material } from "@/api/client.ts";
import { Sparkles, Zap, Thermometer, Leaf } from "lucide-react";
import clsx from "clsx";

interface MaterialCardProps {
  material: Material;
  selected?: boolean;
  onToggleSelect?: (id: string) => void;
}

export default function MaterialCard({
  material,
  selected = false,
  onToggleSelect,
}: MaterialCardProps) {
  const isSmart = material.is_smart ?? false;

  return (
    <div
      className={clsx(
        "bg-surface rounded-xl border p-5 shadow-card hover:shadow-elevated transition-all cursor-pointer",
        isSmart
          ? "border-violet-300 ring-1 ring-violet-200/50"
          : "border-border",
        selected && "ring-2 ring-eco-500 border-eco-400",
      )}
      onClick={() => onToggleSelect?.(material.id)}
    >
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="text-sm font-semibold text-text-heading">
            {material.name}
          </h3>
          <span className="text-xs text-text-tertiary">
            {material.category} &middot; {material.grade}
          </span>
        </div>
        <div className="flex items-center gap-1.5">
          {isSmart && (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-semibold bg-violet-50 text-violet-700 ring-1 ring-inset ring-violet-600/10">
              <Sparkles size={10} />
              Smart
            </span>
          )}
          {selected && (
            <span className="inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-semibold bg-eco-50 text-eco-700 ring-1 ring-inset ring-eco-600/10">
              Selected
            </span>
          )}
        </div>
      </div>

      <div className="space-y-2">
        {material.strength != null && (
          <div className="flex items-center justify-between">
            <span className="flex items-center gap-1.5 text-xs text-text-secondary">
              <Zap size={12} className="text-amber-500" />
              Strength
            </span>
            <span className="text-xs font-medium text-text-primary">
              {material.strength} MPa
            </span>
          </div>
        )}

        {material.thermal_conductivity != null && (
          <div className="flex items-center justify-between">
            <span className="flex items-center gap-1.5 text-xs text-text-secondary">
              <Thermometer size={12} className="text-red-400" />
              Thermal Cond.
            </span>
            <span className="text-xs font-medium text-text-primary">
              {material.thermal_conductivity} W/mK
            </span>
          </div>
        )}

        {material.embodied_carbon != null && (
          <div className="flex items-center justify-between">
            <span className="flex items-center gap-1.5 text-xs text-text-secondary">
              <Leaf size={12} className="text-emerald-500" />
              Embodied Carbon
            </span>
            <span className="text-xs font-medium text-text-primary">
              {material.embodied_carbon} kgCO2/kg
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
