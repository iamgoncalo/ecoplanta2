import { useQuery } from "@tanstack/react-query";
import {
  fetchDeploy,
  fetchDeliverySchedule,
  fetchCommissioning,
} from "@/api/client.ts";
import type { Delivery, DeployJob } from "@/api/client.ts";
import DataTable from "@/components/DataTable.tsx";
import type { Column } from "@/components/DataTable.tsx";
import MetricCard from "@/components/MetricCard.tsx";
import StatusBadge from "@/components/StatusBadge.tsx";
import LoadingState from "@/components/LoadingState.tsx";
import ErrorState from "@/components/ErrorState.tsx";
import ProgressBar from "@/components/ProgressBar.tsx";
import TimelineView from "@/components/TimelineView.tsx";
import ChecklistCard from "@/components/ChecklistCard.tsx";
import {
  Truck,
  Package,
  MapPin,
  CheckCircle,
  Clock,
  Loader2,
  ClipboardCheck,
} from "lucide-react";
import clsx from "clsx";

/* ---- Delivery Columns ---- */

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
    render: (row) => <ProgressBar value={row.progress} size="sm" />,
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

/* ---- Commissioning Overview ---- */

function CommissioningSection() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["commissioning"],
    queryFn: fetchCommissioning,
  });

  if (isLoading) return <LoadingState variant="cards" rows={4} />;
  if (isError || !data)
    return (
      <div className="text-xs text-text-tertiary py-4 text-center">
        Unable to load commissioning data
      </div>
    );

  const s = data.summary;

  return (
    <div className="space-y-5">
      {/* Status Overview Cards */}
      <div className="bg-surface rounded-xl border border-border p-5 shadow-card">
        <h3 className="text-sm font-semibold text-text-heading mb-4 flex items-center gap-2">
          <ClipboardCheck size={14} className="text-text-tertiary" />
          Commissioning Status
        </h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {[
            {
              label: "Total",
              value: s.total,
              icon: Package,
              color: "bg-slate-100 text-slate-700",
            },
            {
              label: "Pending",
              value: s.pending,
              icon: Clock,
              color: "bg-blue-50 text-blue-700",
            },
            {
              label: "In Progress",
              value: s.in_progress,
              icon: Loader2,
              color: "bg-amber-50 text-amber-700",
            },
            {
              label: "Completed",
              value: s.completed,
              icon: CheckCircle,
              color: "bg-emerald-50 text-emerald-700",
            },
          ].map((item) => {
            const Icon = item.icon;
            return (
              <div key={item.label} className="text-center">
                <div
                  className={clsx(
                    "inline-flex items-center justify-center w-14 h-14 rounded-2xl text-lg font-bold mb-2",
                    item.color,
                  )}
                >
                  <div className="flex flex-col items-center">
                    <Icon size={16} className="mb-0.5" />
                    <span className="text-base font-bold">{item.value}</span>
                  </div>
                </div>
                <div className="text-xs text-text-secondary font-medium">
                  {item.label}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Commissioning Checklists */}
      {data.jobs.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-text-heading mb-3 flex items-center gap-2">
            <ClipboardCheck size={14} className="text-text-tertiary" />
            Installation Checklists
          </h3>
          <div className="space-y-3">
            {data.jobs.map((job) => (
              <ChecklistCard
                key={job.id}
                title={`${job.id} - ${job.site}`}
                subtitle={`Started: ${job.started}`}
                status={job.status}
                items={job.checklist}
                progress={job.progress}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

/* ---- Schedule Section ---- */

function ScheduleSection() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["deliverySchedule"],
    queryFn: fetchDeliverySchedule,
  });

  if (isLoading)
    return (
      <div className="bg-surface rounded-xl border border-border p-5 shadow-card h-64 flex items-center justify-center">
        <span className="text-sm text-text-tertiary">Loading schedule...</span>
      </div>
    );
  if (isError || !data)
    return (
      <div className="text-xs text-text-tertiary py-4 text-center">
        Unable to load delivery schedule
      </div>
    );

  return <TimelineView entries={data.scheduled} title="Delivery Schedule" />;
}

/* ---- Main Page ---- */

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
          Delivery tracking, deployment jobs, installation management, and
          commissioning
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

      {/* Schedule Timeline + Active Deliveries side by side */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ScheduleSection />

        {/* Active Deliveries */}
        <div className="bg-surface rounded-xl border border-border p-5 shadow-card">
          <h3 className="text-sm font-semibold text-text-heading mb-4 flex items-center gap-2">
            <Truck size={14} className="text-text-tertiary" />
            Active Deliveries
          </h3>
          {data.deliveries.length === 0 ? (
            <p className="text-sm text-text-tertiary text-center py-8">
              No active deliveries
            </p>
          ) : (
            <div className="space-y-3">
              {data.deliveries.map((d) => (
                <div
                  key={d.id}
                  className="rounded-lg border border-border-light p-3 hover:bg-surface-secondary transition-colors"
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-mono text-text-secondary">
                        {d.id}
                      </span>
                      <StatusBadge label={d.status} />
                    </div>
                    <span className="text-xs text-text-tertiary">
                      ETA: {d.eta}
                    </span>
                  </div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-text-primary flex items-center gap-1.5">
                      <MapPin size={12} className="text-text-tertiary" />
                      {d.destination}
                    </span>
                    <span className="text-xs text-text-secondary">
                      {d.items} items
                    </span>
                  </div>
                  <ProgressBar value={d.progress} size="sm" />
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Full Deliveries Table */}
      <div>
        <h2 className="text-sm font-semibold text-text-heading mb-3">
          All Deliveries
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

      {/* Commissioning Status + Checklists */}
      <CommissioningSection />
    </div>
  );
}
