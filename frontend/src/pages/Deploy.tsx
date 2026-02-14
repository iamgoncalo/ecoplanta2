import { useQuery } from "@tanstack/react-query";
import { fetchDeploy } from "@/api/client.ts";
import type { Delivery, DeployJob } from "@/api/client.ts";
import DataTable from "@/components/DataTable.tsx";
import type { Column } from "@/components/DataTable.tsx";
import MetricCard from "@/components/MetricCard.tsx";
import StatusBadge from "@/components/StatusBadge.tsx";
import LoadingState from "@/components/LoadingState.tsx";
import ErrorState from "@/components/ErrorState.tsx";
import { Truck, Package, MapPin, CheckCircle } from "lucide-react";
import clsx from "clsx";

function ProgressBar({ value }: { value: number }) {
  return (
    <div className="flex items-center gap-2">
      <div className="w-24 h-1.5 bg-surface-tertiary rounded-full overflow-hidden">
        <div
          className={clsx(
            "h-full rounded-full transition-all",
            value >= 90
              ? "bg-success"
              : value >= 50
                ? "bg-eco-500"
                : "bg-warning",
          )}
          style={{ width: `${value}%` }}
        />
      </div>
      <span className="text-xs text-text-secondary">{value}%</span>
    </div>
  );
}

const deliveryColumns: Column<Delivery>[] = [
  { key: "id", header: "ID" },
  { key: "destination", header: "Destination" },
  {
    key: "status",
    header: "Status",
    render: (row) => <StatusBadge label={row.status} />,
  },
  { key: "eta", header: "ETA" },
  {
    key: "progress",
    header: "Progress",
    render: (row) => <ProgressBar value={row.progress} />,
  },
  {
    key: "items",
    header: "Items",
    render: (row) => row.items.toLocaleString(),
  },
];

const jobColumns: Column<DeployJob>[] = [
  { key: "id", header: "Job ID" },
  { key: "site", header: "Site" },
  { key: "type", header: "Type" },
  {
    key: "status",
    header: "Status",
    render: (row) => <StatusBadge label={row.status} />,
  },
  { key: "started", header: "Started" },
  { key: "team", header: "Team" },
];

export default function Deploy() {
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["deploy"],
    queryFn: fetchDeploy,
  });

  if (isLoading) return <LoadingState />;
  if (isError)
    return (
      <ErrorState
        message="Failed to load Deploy data."
        onRetry={() => refetch()}
      />
    );
  if (!data) return null;

  const metrics = data.metrics ?? {};

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-text-heading">Deploy</h1>
        <p className="text-sm text-text-secondary mt-0.5">
          Delivery tracking, deployment jobs, and installation management
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Active Deliveries"
          value={metrics.active_deliveries ?? data.deliveries.length}
          icon={Truck}
        />
        <MetricCard
          title="In Transit"
          value={metrics.in_transit ?? 0}
          icon={Package}
        />
        <MetricCard
          title="Sites Active"
          value={metrics.active_sites ?? 0}
          icon={MapPin}
        />
        <MetricCard
          title="Completed"
          value={metrics.completed ?? 0}
          icon={CheckCircle}
          trend="up"
        />
      </div>

      {/* Deliveries Overview */}
      <div>
        <h2 className="text-sm font-semibold text-text-heading mb-3">
          Active Deliveries
        </h2>
        <DataTable
          columns={deliveryColumns}
          data={data.deliveries}
          keyExtractor={(row) => row.id}
          emptyMessage="No active deliveries"
        />
      </div>

      {/* Deployment Jobs */}
      <div>
        <h2 className="text-sm font-semibold text-text-heading mb-3">
          Deployment Jobs
        </h2>
        <DataTable
          columns={jobColumns}
          data={data.jobs}
          keyExtractor={(row) => row.id}
          emptyMessage="No deployment jobs"
        />
      </div>

      {/* Installation Status */}
      <div className="bg-surface rounded-xl border border-border p-5 shadow-card">
        <h3 className="text-sm font-semibold text-text-heading mb-4">
          Installation Overview
        </h3>
        <div className="grid grid-cols-3 gap-4">
          {[
            {
              label: "Scheduled",
              value: metrics.installations_scheduled ?? 0,
              color: "bg-blue-100 text-blue-700",
            },
            {
              label: "In Progress",
              value: metrics.installations_in_progress ?? 0,
              color: "bg-amber-100 text-amber-700",
            },
            {
              label: "Completed",
              value: metrics.installations_completed ?? 0,
              color: "bg-emerald-100 text-emerald-700",
            },
          ].map((item) => (
            <div key={item.label} className="text-center">
              <div
                className={clsx(
                  "inline-flex items-center justify-center w-14 h-14 rounded-2xl text-lg font-bold mb-2",
                  item.color,
                )}
              >
                {item.value}
              </div>
              <div className="text-xs text-text-secondary font-medium">
                {item.label}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
