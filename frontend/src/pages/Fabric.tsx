import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  fetchFabric,
  fetchFabricScene,
  fetchWorkOrders,
  fetchWorkOrder,
  fetchInventory,
  fetchQARecords,
} from "@/api/client.ts";
import type {
  ProductionLine,
  WorkOrder,
  WorkOrderDetail,
  InventoryItem,
  QARecord,
} from "@/api/client.ts";
import Scene3D from "@/components/Scene3D.tsx";
import DataTable from "@/components/DataTable.tsx";
import type { Column } from "@/components/DataTable.tsx";
import MetricCard from "@/components/MetricCard.tsx";
import StatusBadge from "@/components/StatusBadge.tsx";
import LoadingState from "@/components/LoadingState.tsx";
import ErrorState from "@/components/ErrorState.tsx";
import ProgressBar from "@/components/ProgressBar.tsx";
import {
  Factory,
  Zap,
  BarChart3,
  ClipboardList,
  ChevronDown,
  ChevronRight,
  Package,
  AlertTriangle,
  ShieldCheck,
  Layers,
} from "lucide-react";
import clsx from "clsx";

/* ---- Work Order Expandable Row ---- */

function WorkOrderExpanded({ orderId }: { orderId: string }) {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["workorder", orderId],
    queryFn: () => fetchWorkOrder(orderId),
  });

  if (isLoading)
    return (
      <div className="px-6 py-4 text-xs text-text-tertiary">
        Loading details...
      </div>
    );
  if (isError || !data)
    return (
      <div className="px-6 py-4 text-xs text-danger">
        Failed to load details.
      </div>
    );

  const detail = data as WorkOrderDetail;

  return (
    <div className="px-6 py-4 bg-surface-secondary border-t border-border-light">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* BOM */}
        <div>
          <h4 className="text-xs font-semibold text-text-heading mb-2 flex items-center gap-1.5">
            <Layers size={12} className="text-text-tertiary" />
            Bill of Materials
          </h4>
          {detail.bom && detail.bom.length > 0 ? (
            <div className="overflow-x-auto rounded-lg border border-border-light">
              <table className="w-full text-xs">
                <thead>
                  <tr className="bg-surface-tertiary">
                    <th className="px-3 py-2 text-left font-semibold text-text-secondary">
                      Material
                    </th>
                    <th className="px-3 py-2 text-left font-semibold text-text-secondary">
                      Qty
                    </th>
                    <th className="px-3 py-2 text-left font-semibold text-text-secondary">
                      Unit
                    </th>
                    <th className="px-3 py-2 text-left font-semibold text-text-secondary">
                      Unit Cost
                    </th>
                    <th className="px-3 py-2 text-left font-semibold text-text-secondary">
                      Total
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {detail.bom.map((item, idx) => (
                    <tr
                      key={idx}
                      className="border-t border-border-light hover:bg-surface-secondary"
                    >
                      <td className="px-3 py-2 text-text-primary">
                        {item.material}
                      </td>
                      <td className="px-3 py-2 tabular-nums">{item.quantity}</td>
                      <td className="px-3 py-2">{item.unit}</td>
                      <td className="px-3 py-2 tabular-nums">
                        ${item.unit_cost.toFixed(2)}
                      </td>
                      <td className="px-3 py-2 font-medium tabular-nums">
                        ${(item.quantity * item.unit_cost).toFixed(2)}
                      </td>
                    </tr>
                  ))}
                </tbody>
                <tfoot>
                  <tr className="border-t border-border bg-surface-tertiary">
                    <td
                      colSpan={4}
                      className="px-3 py-2 font-semibold text-text-heading text-right"
                    >
                      Total Cost
                    </td>
                    <td className="px-3 py-2 font-bold text-text-heading tabular-nums">
                      $
                      {detail.bom
                        .reduce((s, b) => s + b.quantity * b.unit_cost, 0)
                        .toFixed(2)}
                    </td>
                  </tr>
                </tfoot>
              </table>
            </div>
          ) : (
            <p className="text-xs text-text-tertiary">No BOM data</p>
          )}
        </div>

        {/* QA Records */}
        <div>
          <h4 className="text-xs font-semibold text-text-heading mb-2 flex items-center gap-1.5">
            <ShieldCheck size={12} className="text-text-tertiary" />
            QA Records
          </h4>
          {detail.qa_records && detail.qa_records.length > 0 ? (
            <div className="space-y-2">
              {detail.qa_records.map((qa) => (
                <div
                  key={qa.id}
                  className="rounded-lg border border-border-light p-3 bg-surface"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-medium text-text-primary">
                      {qa.inspector}
                    </span>
                    <StatusBadge label={qa.result} />
                  </div>
                  <div className="text-[10px] text-text-tertiary">{qa.date}</div>
                  {qa.defects.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-1.5">
                      {qa.defects.map((d, di) => (
                        <span
                          key={di}
                          className="inline-flex px-1.5 py-0.5 bg-red-50 text-red-600 rounded text-[10px] font-medium"
                        >
                          {d}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-text-tertiary">No QA records</p>
          )}
        </div>
      </div>
    </div>
  );
}

/* ---- Inventory Dashboard ---- */

function InventoryDashboard() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["inventory"],
    queryFn: fetchInventory,
  });

  if (isLoading)
    return <LoadingState variant="table" rows={4} />;
  if (isError || !data)
    return (
      <div className="text-xs text-text-tertiary py-4 text-center">
        Unable to load inventory
      </div>
    );

  function stockColor(item: InventoryItem): string {
    const s = item.status.toLowerCase();
    if (s.includes("critical") || s.includes("out"))
      return "bg-red-50 border-red-200";
    if (s.includes("low")) return "bg-amber-50 border-amber-200";
    return "";
  }

  function dotColor(item: InventoryItem): string {
    const s = item.status.toLowerCase();
    if (s.includes("critical") || s.includes("out")) return "bg-[#ef4444]";
    if (s.includes("low")) return "bg-[#eab308]";
    return "bg-[#22c55e]";
  }

  return (
    <div className="bg-surface rounded-xl border border-border p-5 shadow-card">
      <h3 className="text-sm font-semibold text-text-heading mb-4 flex items-center gap-2">
        <Package size={14} className="text-text-tertiary" />
        Inventory Levels
      </h3>

      {/* Reorder alerts */}
      {data.alerts.length > 0 && (
        <div className="mb-4 space-y-2">
          {data.alerts.map((a, i) => (
            <div
              key={i}
              className={clsx(
                "flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium",
                a.severity === "critical"
                  ? "bg-red-50 text-red-700"
                  : "bg-amber-50 text-amber-700",
              )}
            >
              <AlertTriangle size={12} />
              <span>
                {a.material}: {a.message}
              </span>
            </div>
          ))}
        </div>
      )}

      <div className="overflow-x-auto rounded-lg border border-border-light">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-surface-secondary border-b border-border">
              <th className="px-4 py-3 text-left text-xs font-semibold text-text-secondary uppercase tracking-wider">
                Material
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-text-secondary uppercase tracking-wider">
                Stock
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-text-secondary uppercase tracking-wider">
                Reorder Level
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-text-secondary uppercase tracking-wider">
                Status
              </th>
            </tr>
          </thead>
          <tbody>
            {data.items.map((item) => (
              <tr
                key={item.id}
                className={clsx(
                  "border-b border-border-light last:border-b-0 hover:bg-surface-secondary transition-colors",
                  stockColor(item),
                )}
              >
                <td className="px-4 py-3 text-text-primary font-medium">
                  {item.material}
                </td>
                <td className="px-4 py-3 tabular-nums">
                  {item.quantity.toLocaleString()} {item.unit}
                </td>
                <td className="px-4 py-3 tabular-nums text-text-secondary">
                  {item.reorder_level.toLocaleString()} {item.unit}
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <div
                      className={clsx(
                        "w-2 h-2 rounded-full",
                        dotColor(item),
                      )}
                    />
                    <span className="text-xs font-medium text-text-secondary capitalize">
                      {item.status}
                    </span>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

/* ---- QA Summary Panel ---- */

function QASummaryPanel() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["qaRecords"],
    queryFn: fetchQARecords,
  });

  if (isLoading) return <LoadingState variant="cards" rows={3} />;
  if (isError || !data)
    return (
      <div className="text-xs text-text-tertiary py-4 text-center">
        Unable to load QA data
      </div>
    );

  const summary = data.summary;

  return (
    <div className="bg-surface rounded-xl border border-border p-5 shadow-card">
      <h3 className="text-sm font-semibold text-text-heading mb-4 flex items-center gap-2">
        <ShieldCheck size={14} className="text-text-tertiary" />
        QA Summary
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-5">
        {/* Pass Rate Gauge */}
        <div className="flex flex-col items-center justify-center p-4 rounded-lg bg-surface-secondary border border-border-light">
          <div className="relative w-20 h-20 mb-2">
            <svg viewBox="0 0 36 36" className="w-20 h-20 -rotate-90">
              <circle
                cx="18"
                cy="18"
                r="15.5"
                fill="none"
                stroke="#f1f5f9"
                strokeWidth="3"
              />
              <circle
                cx="18"
                cy="18"
                r="15.5"
                fill="none"
                stroke={summary.pass_rate >= 90 ? "#22c55e" : summary.pass_rate >= 70 ? "#eab308" : "#ef4444"}
                strokeWidth="3"
                strokeLinecap="round"
                strokeDasharray={`${summary.pass_rate * 0.9735} 100`}
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-lg font-bold text-text-heading tabular-nums">
                {summary.pass_rate}%
              </span>
            </div>
          </div>
          <span className="text-xs text-text-secondary font-medium">
            Pass Rate
          </span>
        </div>

        {/* Total Inspections */}
        <div className="flex flex-col items-center justify-center p-4 rounded-lg bg-surface-secondary border border-border-light">
          <span className="text-2xl font-bold text-text-heading tabular-nums">
            {summary.total_inspections}
          </span>
          <span className="text-xs text-text-secondary font-medium mt-1">
            Total Inspections
          </span>
        </div>

        {/* Common Defects */}
        <div className="p-4 rounded-lg bg-surface-secondary border border-border-light">
          <h4 className="text-xs font-semibold text-text-heading mb-2">
            Common Defects
          </h4>
          {summary.common_defects.length === 0 ? (
            <p className="text-xs text-text-tertiary">No defects recorded</p>
          ) : (
            <ul className="space-y-1.5">
              {summary.common_defects.slice(0, 5).map((d) => (
                <li
                  key={d.defect}
                  className="flex items-center justify-between text-xs"
                >
                  <span className="text-text-secondary truncate mr-2">
                    {d.defect}
                  </span>
                  <span className="text-text-heading font-semibold tabular-nums shrink-0">
                    {d.count}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      {/* Recent QA Records */}
      <h4 className="text-xs font-semibold text-text-heading mb-2">
        Recent QA Records
      </h4>
      {data.records.length === 0 ? (
        <p className="text-xs text-text-tertiary text-center py-4">
          No QA records
        </p>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-border-light">
          <table className="w-full text-xs">
            <thead>
              <tr className="bg-surface-secondary border-b border-border">
                <th className="px-3 py-2 text-left font-semibold text-text-secondary">
                  ID
                </th>
                <th className="px-3 py-2 text-left font-semibold text-text-secondary">
                  Work Order
                </th>
                <th className="px-3 py-2 text-left font-semibold text-text-secondary">
                  Inspector
                </th>
                <th className="px-3 py-2 text-left font-semibold text-text-secondary">
                  Result
                </th>
                <th className="px-3 py-2 text-left font-semibold text-text-secondary">
                  Date
                </th>
              </tr>
            </thead>
            <tbody>
              {data.records.slice(0, 10).map((qa: QARecord) => (
                <tr
                  key={qa.id}
                  className="border-t border-border-light hover:bg-surface-secondary transition-colors"
                >
                  <td className="px-3 py-2 text-text-primary font-mono">
                    {qa.id}
                  </td>
                  <td className="px-3 py-2 text-text-secondary">
                    {qa.work_order_id}
                  </td>
                  <td className="px-3 py-2 text-text-primary">{qa.inspector}</td>
                  <td className="px-3 py-2">
                    <StatusBadge label={qa.result} />
                  </td>
                  <td className="px-3 py-2 text-text-secondary">{qa.date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

/* ---- Column Definitions ---- */

const lineColumns: Column<ProductionLine>[] = [
  { key: "name", header: "Line" },
  { key: "product", header: "Product" },
  {
    key: "status",
    header: "Status",
    render: (row) => <StatusBadge label={row.status} />,
  },
  {
    key: "throughput",
    header: "Throughput",
    render: (row) => <span>{row.throughput} units/hr</span>,
  },
  {
    key: "efficiency",
    header: "Efficiency",
    render: (row) => (
      <ProgressBar value={row.efficiency} size="sm" />
    ),
  },
];

/* ---- Main Page ---- */

export default function Fabric() {
  const [expandedOrder, setExpandedOrder] = useState<string | null>(null);

  const fabric = useQuery({ queryKey: ["fabric"], queryFn: fetchFabric });
  const scene = useQuery({
    queryKey: ["fabric-scene"],
    queryFn: fetchFabricScene,
  });
  const workOrders = useQuery({
    queryKey: ["workOrders"],
    queryFn: fetchWorkOrders,
  });

  if (fabric.isLoading) return <LoadingState />;
  if (fabric.isError)
    return (
      <ErrorState
        message="Failed to load Fabric data."
        onRetry={() => fabric.refetch()}
      />
    );

  const data = fabric.data;
  if (!data) return null;

  const metrics = data.metrics ?? {};

  // Use extended work orders if available, fallback to fabric data
  const orders: WorkOrder[] = workOrders.data?.work_orders ?? data.work_orders;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-text-heading">Fabric</h1>
        <p className="text-sm text-text-secondary mt-0.5">
          Factory operations, production monitoring, inventory, and quality
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Active Lines"
          value={metrics.active_lines ?? data.production_lines.length}
          icon={Factory}
          change={metrics.lines_change as number | undefined}
          trend="up"
        />
        <MetricCard
          title="Avg Efficiency"
          value={`${metrics.avg_efficiency ?? 0}%`}
          icon={Zap}
          change={metrics.efficiency_change as number | undefined}
          trend="up"
        />
        <MetricCard
          title="Total Throughput"
          value={metrics.total_throughput ?? 0}
          unit="units/hr"
          icon={BarChart3}
        />
        <MetricCard
          title="Open Orders"
          value={metrics.open_orders ?? data.work_orders.length}
          icon={ClipboardList}
        />
      </div>

      {/* 3D Scene */}
      {scene.data && <Scene3D objects={scene.data.objects} />}
      {scene.isLoading && (
        <div className="w-full h-[400px] rounded-xl border border-border bg-surface flex items-center justify-center">
          <span className="text-sm text-text-tertiary">
            Loading 3D scene...
          </span>
        </div>
      )}

      {/* Production Lines */}
      <div>
        <h2 className="text-sm font-semibold text-text-heading mb-3">
          Production Lines
        </h2>
        <DataTable
          columns={lineColumns}
          data={data.production_lines}
          keyExtractor={(row) => row.id}
          emptyMessage="No production lines configured"
        />
      </div>

      {/* Work Orders (Expandable) */}
      <div>
        <h2 className="text-sm font-semibold text-text-heading mb-3">
          Work Orders
        </h2>
        <div className="overflow-x-auto rounded-lg border border-border bg-surface">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border bg-surface-secondary">
                <th className="px-4 py-3 text-left text-xs font-semibold text-text-secondary uppercase tracking-wider w-8" />
                <th className="px-4 py-3 text-left text-xs font-semibold text-text-secondary uppercase tracking-wider">
                  Order ID
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-text-secondary uppercase tracking-wider">
                  Product
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-text-secondary uppercase tracking-wider">
                  Quantity
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-text-secondary uppercase tracking-wider">
                  Status
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-text-secondary uppercase tracking-wider">
                  Priority
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-text-secondary uppercase tracking-wider">
                  Due Date
                </th>
              </tr>
            </thead>
            <tbody>
              {orders.length === 0 ? (
                <tr>
                  <td
                    colSpan={7}
                    className="px-4 py-12 text-center text-text-tertiary"
                  >
                    No active work orders
                  </td>
                </tr>
              ) : (
                orders.map((order) => {
                  const isExpanded = expandedOrder === order.id;
                  return (
                    <tr key={order.id} className="contents">
                      <tr
                        className={clsx(
                          "border-b border-border-light hover:bg-surface-secondary transition-colors cursor-pointer",
                          isExpanded && "bg-surface-secondary",
                        )}
                        onClick={() =>
                          setExpandedOrder(isExpanded ? null : order.id)
                        }
                      >
                        <td className="px-4 py-3 text-text-tertiary">
                          {isExpanded ? (
                            <ChevronDown size={14} />
                          ) : (
                            <ChevronRight size={14} />
                          )}
                        </td>
                        <td className="px-4 py-3 text-text-primary font-mono text-xs">
                          {order.id}
                        </td>
                        <td className="px-4 py-3 text-text-primary">
                          {order.product}
                        </td>
                        <td className="px-4 py-3 tabular-nums">
                          {order.quantity.toLocaleString()}
                        </td>
                        <td className="px-4 py-3">
                          <StatusBadge label={order.status} />
                        </td>
                        <td className="px-4 py-3">
                          <StatusBadge label={order.priority} />
                        </td>
                        <td className="px-4 py-3 text-text-secondary">
                          {order.due_date}
                        </td>
                      </tr>
                      {isExpanded && (
                        <tr>
                          <td colSpan={7} className="p-0">
                            <WorkOrderExpanded orderId={order.id} />
                          </td>
                        </tr>
                      )}
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Inventory Dashboard */}
      <InventoryDashboard />

      {/* QA Summary */}
      <QASummaryPanel />
    </div>
  );
}
