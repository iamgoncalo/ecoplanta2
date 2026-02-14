import { useQuery } from "@tanstack/react-query";
import { fetchSales } from "@/api/client.ts";
import type { Lead, PipelineStage } from "@/api/client.ts";
import DataTable from "@/components/DataTable.tsx";
import type { Column } from "@/components/DataTable.tsx";
import MetricCard from "@/components/MetricCard.tsx";
import StatusBadge from "@/components/StatusBadge.tsx";
import LoadingState from "@/components/LoadingState.tsx";
import ErrorState from "@/components/ErrorState.tsx";
import {
  DollarSign,
  Percent,
  BarChart3,
  TrendingUp,
} from "lucide-react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";
import clsx from "clsx";

function formatCurrency(value: number): string {
  if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(1)}M`;
  if (value >= 1_000) return `$${(value / 1_000).toFixed(0)}K`;
  return `$${value}`;
}

function PipelineViz({ stages }: { stages: PipelineStage[] }) {
  const maxValue = Math.max(...stages.map((s) => s.value), 1);

  return (
    <div className="bg-surface rounded-xl border border-border p-5 shadow-card">
      <h3 className="text-sm font-semibold text-text-heading mb-4">
        Pipeline Stages
      </h3>
      <div className="space-y-3">
        {stages.map((stage, i) => (
          <div key={stage.name} className="flex items-center gap-3">
            <div className="w-28 text-xs text-text-secondary font-medium truncate">
              {stage.name}
            </div>
            <div className="flex-1 h-7 bg-surface-tertiary rounded-md overflow-hidden relative">
              <div
                className={clsx(
                  "h-full rounded-md transition-all duration-500",
                  i === 0 && "bg-blue-200",
                  i === 1 && "bg-blue-300",
                  i === 2 && "bg-blue-400",
                  i === 3 && "bg-blue-500",
                  i >= 4 && "bg-eco-600",
                )}
                style={{
                  width: `${(stage.value / maxValue) * 100}%`,
                }}
              />
              <div className="absolute inset-0 flex items-center px-3">
                <span className="text-[10px] font-semibold text-slate-700">
                  {stage.count} deals - {formatCurrency(stage.value)}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

const leadColumns: Column<Lead>[] = [
  { key: "company", header: "Company" },
  { key: "contact", header: "Contact" },
  {
    key: "score",
    header: "Score",
    render: (row) => (
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 rounded-full border-2 border-eco-200 flex items-center justify-center">
          <span
            className={clsx(
              "text-xs font-bold",
              row.score >= 80
                ? "text-success"
                : row.score >= 50
                  ? "text-eco-600"
                  : "text-warning",
            )}
          >
            {row.score}
          </span>
        </div>
      </div>
    ),
  },
  {
    key: "stage",
    header: "Stage",
    render: (row) => <StatusBadge label={row.stage} />,
  },
  {
    key: "value",
    header: "Value",
    render: (row) => (
      <span className="font-medium">{formatCurrency(row.value)}</span>
    ),
  },
  { key: "last_activity", header: "Last Activity" },
];

export default function Sales() {
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["sales"],
    queryFn: fetchSales,
  });

  if (isLoading) return <LoadingState />;
  if (isError)
    return (
      <ErrorState
        message="Failed to load Sales data."
        onRetry={() => refetch()}
      />
    );
  if (!data) return null;

  const m = data.metrics;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-text-heading">Sales</h1>
        <p className="text-sm text-text-secondary mt-0.5">
          Pipeline management, leads, and revenue tracking
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Revenue"
          value={formatCurrency(m.total_revenue)}
          icon={DollarSign}
          trend="up"
        />
        <MetricCard
          title="Conversion Rate"
          value={`${m.conversion_rate}%`}
          icon={Percent}
          trend="up"
        />
        <MetricCard
          title="Avg Deal Size"
          value={formatCurrency(m.avg_deal_size)}
          icon={BarChart3}
        />
        <MetricCard
          title="Pipeline Value"
          value={formatCurrency(m.pipeline_value)}
          icon={TrendingUp}
        />
      </div>

      {/* Pipeline + Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <PipelineViz stages={data.pipeline} />

        {/* Revenue Chart */}
        <div className="bg-surface rounded-xl border border-border p-5 shadow-card">
          <h3 className="text-sm font-semibold text-text-heading mb-4">
            Revenue Trend
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data.revenue_chart}>
                <defs>
                  <linearGradient id="revGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#2563eb" stopOpacity={0.1} />
                    <stop offset="95%" stopColor="#2563eb" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis
                  dataKey="month"
                  tick={{ fontSize: 11, fill: "#94a3b8" }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  tick={{ fontSize: 11, fill: "#94a3b8" }}
                  axisLine={false}
                  tickLine={false}
                  tickFormatter={(v: number) => formatCurrency(v)}
                />
                <Tooltip
                  contentStyle={{
                    borderRadius: "8px",
                    border: "1px solid #e2e8f0",
                    boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.05)",
                    fontSize: "12px",
                  }}
                  formatter={(value) => [formatCurrency(value as number), ""]}
                />
                <Legend
                  wrapperStyle={{ fontSize: "11px", paddingTop: "8px" }}
                />
                <Area
                  type="monotone"
                  dataKey="revenue"
                  stroke="#2563eb"
                  strokeWidth={2}
                  fill="url(#revGrad)"
                  name="Revenue"
                />
                <Area
                  type="monotone"
                  dataKey="target"
                  stroke="#94a3b8"
                  strokeWidth={1}
                  strokeDasharray="4 4"
                  fill="none"
                  name="Target"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Leads Table */}
      <div>
        <h2 className="text-sm font-semibold text-text-heading mb-3">Leads</h2>
        <DataTable
          columns={leadColumns}
          data={data.leads}
          keyExtractor={(row) => row.id}
          emptyMessage="No leads in pipeline"
        />
      </div>
    </div>
  );
}
