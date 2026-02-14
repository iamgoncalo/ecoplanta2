import type { OptimizationResult } from "@/api/client.ts";
import { ArrowRight, TrendingUp } from "lucide-react";
import clsx from "clsx";

interface AllocationViewProps {
  result: OptimizationResult;
}

export default function AllocationView({ result }: AllocationViewProps) {
  return (
    <div className="space-y-4">
      {/* Summary metrics */}
      {(result.optimization_score != null ||
        result.total_cost_savings != null) && (
        <div className="flex items-center gap-4">
          {result.optimization_score != null && (
            <div className="flex items-center gap-2 bg-emerald-50 text-emerald-700 rounded-lg px-3 py-2">
              <TrendingUp size={14} />
              <span className="text-xs font-semibold">
                Optimization Score: {result.optimization_score}%
              </span>
            </div>
          )}
          {result.total_cost_savings != null && (
            <div className="flex items-center gap-2 bg-blue-50 text-blue-700 rounded-lg px-3 py-2">
              <span className="text-xs font-semibold">
                Estimated Savings: ${result.total_cost_savings.toLocaleString()}
              </span>
            </div>
          )}
        </div>
      )}

      {/* Allocation cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {result.allocations.map((alloc) => (
          <div
            key={alloc.partner_id}
            className="bg-surface rounded-xl border border-border p-4 shadow-card"
          >
            <div className="flex items-start justify-between mb-3">
              <div>
                <h4 className="text-sm font-semibold text-text-heading">
                  {alloc.partner_name}
                </h4>
                <span className="text-xs text-text-tertiary">
                  ID: {alloc.partner_id}
                </span>
              </div>
              <div className="flex items-center gap-1.5">
                <div
                  className={clsx(
                    "w-2 h-2 rounded-full",
                    alloc.utilization >= 80
                      ? "bg-danger"
                      : alloc.utilization >= 50
                        ? "bg-warning"
                        : "bg-success",
                  )}
                />
                <span className="text-xs font-medium text-text-secondary">
                  {alloc.utilization}% util.
                </span>
              </div>
            </div>

            {/* Orders assigned */}
            {alloc.orders.length > 0 && (
              <div className="mb-3">
                <span className="text-xs text-text-secondary font-medium">
                  Assigned Orders:
                </span>
                <div className="flex flex-wrap gap-1.5 mt-1">
                  {alloc.orders.map((order) => (
                    <span
                      key={order}
                      className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-medium bg-surface-secondary text-text-primary ring-1 ring-inset ring-border"
                    >
                      <ArrowRight size={8} />
                      {order}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Reasoning */}
            <div className="bg-surface-secondary rounded-lg p-3">
              <p className="text-xs text-text-secondary">{alloc.reasoning}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
