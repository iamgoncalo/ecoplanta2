import { useQuery } from "@tanstack/react-query";
import { fetchFabric, fetchFabricScene } from "@/api/client.ts";
import type { ProductionLine, WorkOrder } from "@/api/client.ts";
import Scene3D from "@/components/Scene3D.tsx";
import DataTable from "@/components/DataTable.tsx";
import type { Column } from "@/components/DataTable.tsx";
import MetricCard from "@/components/MetricCard.tsx";
import StatusBadge from "@/components/StatusBadge.tsx";
import LoadingState from "@/components/LoadingState.tsx";
import ErrorState from "@/components/ErrorState.tsx";
import { Factory, Zap, BarChart3, ClipboardList } from "lucide-react";

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
      <div className="flex items-center gap-2">
        <div className="w-16 h-1.5 bg-surface-tertiary rounded-full overflow-hidden">
          <div
            className="h-full bg-eco-600 rounded-full"
            style={{ width: `${row.efficiency}%` }}
          />
        </div>
        <span className="text-xs text-text-secondary">{row.efficiency}%</span>
      </div>
    ),
  },
];

const orderColumns: Column<WorkOrder>[] = [
  { key: "id", header: "Order ID" },
  { key: "product", header: "Product" },
  {
    key: "quantity",
    header: "Quantity",
    render: (row) => row.quantity.toLocaleString(),
  },
  {
    key: "status",
    header: "Status",
    render: (row) => <StatusBadge label={row.status} />,
  },
  {
    key: "priority",
    header: "Priority",
    render: (row) => <StatusBadge label={row.priority} />,
  },
  { key: "due_date", header: "Due Date" },
];

export default function Fabric() {
  const fabric = useQuery({ queryKey: ["fabric"], queryFn: fetchFabric });
  const scene = useQuery({
    queryKey: ["fabric-scene"],
    queryFn: fetchFabricScene,
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

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-text-heading">Fabric</h1>
        <p className="text-sm text-text-secondary mt-0.5">
          Factory operations and production monitoring
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
          <span className="text-sm text-text-tertiary">Loading 3D scene...</span>
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

      {/* Work Orders */}
      <div>
        <h2 className="text-sm font-semibold text-text-heading mb-3">
          Work Orders
        </h2>
        <DataTable
          columns={orderColumns}
          data={data.work_orders}
          keyExtractor={(row) => row.id}
          emptyMessage="No active work orders"
        />
      </div>
    </div>
  );
}
