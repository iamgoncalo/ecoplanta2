import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  fetchSales,
  fetchSalesPipeline,
  createLead,
} from "@/api/client.ts";
import type { Lead, PipelineStage, CreateLeadPayload } from "@/api/client.ts";
import DataTable from "@/components/DataTable.tsx";
import type { Column } from "@/components/DataTable.tsx";
import MetricCard from "@/components/MetricCard.tsx";
import StatusBadge from "@/components/StatusBadge.tsx";
import LoadingState from "@/components/LoadingState.tsx";
import ErrorState from "@/components/ErrorState.tsx";
import FunnelChart from "@/components/FunnelChart.tsx";
import {
  DollarSign,
  Percent,
  BarChart3,
  TrendingUp,
  Plus,
  X,
  ArrowRight,
  MapPin,
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

/* ---- Pipeline bar (kept from v1) ---- */

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

/* ---- Conversion Metrics ---- */

function ConversionMetrics({
  conversions,
}: {
  conversions: { from: string; to: string; rate: number }[];
}) {
  return (
    <div className="bg-surface rounded-xl border border-border p-5 shadow-card">
      <h3 className="text-sm font-semibold text-text-heading mb-4">
        Conversion Rates
      </h3>
      {conversions.length === 0 ? (
        <p className="text-xs text-text-tertiary text-center py-4">
          No conversion data
        </p>
      ) : (
        <div className="space-y-3">
          {conversions.map((c) => (
            <div
              key={`${c.from}-${c.to}`}
              className="flex items-center gap-2 text-xs"
            >
              <span className="text-text-secondary font-medium min-w-[80px] truncate">
                {c.from}
              </span>
              <ArrowRight size={12} className="text-text-tertiary shrink-0" />
              <span className="text-text-secondary font-medium min-w-[80px] truncate">
                {c.to}
              </span>
              <div className="flex-1 h-2 bg-surface-tertiary rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full bg-[#2563eb] transition-all duration-500"
                  style={{ width: `${c.rate}%` }}
                />
              </div>
              <span className="text-text-heading font-semibold tabular-nums min-w-[40px] text-right">
                {c.rate}%
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/* ---- Territory Breakdown ---- */

function TerritoryBreakdown({
  territories,
}: {
  territories: { region: string; lead_count: number; value: number }[];
}) {
  return (
    <div className="bg-surface rounded-xl border border-border p-5 shadow-card">
      <h3 className="text-sm font-semibold text-text-heading mb-4 flex items-center gap-2">
        <MapPin size={14} className="text-text-tertiary" />
        Portugal Territory Breakdown
      </h3>
      {territories.length === 0 ? (
        <p className="text-xs text-text-tertiary text-center py-4">
          No territory data
        </p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {territories.map((t) => (
            <div
              key={t.region}
              className="rounded-lg border border-border-light bg-surface-secondary p-4 hover:bg-surface-tertiary transition-colors"
            >
              <h4 className="text-sm font-semibold text-text-heading">
                {t.region}
              </h4>
              <div className="flex items-center gap-4 mt-2">
                <div>
                  <span className="text-lg font-bold text-[#2563eb] tabular-nums">
                    {t.lead_count}
                  </span>
                  <span className="text-[10px] text-text-tertiary ml-1">
                    leads
                  </span>
                </div>
                <div className="h-6 w-px bg-border" />
                <div>
                  <span className="text-lg font-bold text-text-heading tabular-nums">
                    {formatCurrency(t.value)}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/* ---- New Lead Modal ---- */

function NewLeadModal({ onClose }: { onClose: () => void }) {
  const queryClient = useQueryClient();
  const [form, setForm] = useState<CreateLeadPayload>({
    company: "",
    contact: "",
    value: 0,
    stage: "Discovery",
  });

  const mutation = useMutation({
    mutationFn: createLead,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["sales"] });
      void queryClient.invalidateQueries({ queryKey: ["salesPipeline"] });
      onClose();
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate(form);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm">
      <div className="bg-surface rounded-2xl border border-border shadow-modal w-full max-w-md mx-4 animate-fade-in">
        <div className="flex items-center justify-between px-6 py-4 border-b border-border">
          <h3 className="text-sm font-semibold text-text-heading">
            New Lead
          </h3>
          <button
            type="button"
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-surface-tertiary text-text-tertiary transition-colors"
          >
            <X size={16} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-xs font-semibold text-text-secondary mb-1">
              Company
            </label>
            <input
              type="text"
              required
              value={form.company}
              onChange={(e) =>
                setForm((p) => ({ ...p, company: e.target.value }))
              }
              className="w-full px-3 py-2 text-sm rounded-lg border border-border bg-surface-secondary text-text-primary focus:outline-none focus:ring-2 focus:ring-eco-400/30 focus:border-eco-400 transition-colors"
              placeholder="Company name"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-text-secondary mb-1">
              Contact
            </label>
            <input
              type="text"
              required
              value={form.contact}
              onChange={(e) =>
                setForm((p) => ({ ...p, contact: e.target.value }))
              }
              className="w-full px-3 py-2 text-sm rounded-lg border border-border bg-surface-secondary text-text-primary focus:outline-none focus:ring-2 focus:ring-eco-400/30 focus:border-eco-400 transition-colors"
              placeholder="Contact person"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-text-secondary mb-1">
              Value ($)
            </label>
            <input
              type="number"
              required
              min={0}
              value={form.value || ""}
              onChange={(e) =>
                setForm((p) => ({
                  ...p,
                  value: Number(e.target.value),
                }))
              }
              className="w-full px-3 py-2 text-sm rounded-lg border border-border bg-surface-secondary text-text-primary focus:outline-none focus:ring-2 focus:ring-eco-400/30 focus:border-eco-400 transition-colors"
              placeholder="Deal value"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-text-secondary mb-1">
              Stage
            </label>
            <select
              value={form.stage}
              onChange={(e) =>
                setForm((p) => ({ ...p, stage: e.target.value }))
              }
              className="w-full px-3 py-2 text-sm rounded-lg border border-border bg-surface-secondary text-text-primary focus:outline-none focus:ring-2 focus:ring-eco-400/30 focus:border-eco-400 transition-colors"
            >
              <option>Discovery</option>
              <option>Proposal</option>
              <option>Negotiation</option>
              <option>Won</option>
              <option>Lost</option>
            </select>
          </div>

          {mutation.isError && (
            <p className="text-xs text-danger">
              Failed to create lead. Please try again.
            </p>
          )}

          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-text-secondary hover:bg-surface-tertiary rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={mutation.isPending}
              className="px-4 py-2 text-sm font-medium text-white bg-[#2563eb] hover:bg-blue-700 rounded-lg transition-colors disabled:opacity-50"
            >
              {mutation.isPending ? "Creating..." : "Create Lead"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

/* ---- Lead Columns ---- */

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

/* ---- Main Page ---- */

export default function Sales() {
  const [showNewLead, setShowNewLead] = useState(false);

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["sales"],
    queryFn: fetchSales,
  });

  const pipeline = useQuery({
    queryKey: ["salesPipeline"],
    queryFn: fetchSalesPipeline,
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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-text-heading">Sales</h1>
          <p className="text-sm text-text-secondary mt-0.5">
            Pipeline management, leads, and revenue tracking
          </p>
        </div>
        <button
          type="button"
          onClick={() => setShowNewLead(true)}
          className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-[#2563eb] hover:bg-blue-700 rounded-lg transition-colors shadow-sm"
        >
          <Plus size={14} />
          New Lead
        </button>
      </div>

      {showNewLead && <NewLeadModal onClose={() => setShowNewLead(false)} />}

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

      {/* Funnel + Pipeline Bars */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {pipeline.data ? (
          <FunnelChart stages={pipeline.data.stages} />
        ) : pipeline.isLoading ? (
          <div className="bg-surface rounded-xl border border-border p-5 shadow-card h-72 flex items-center justify-center">
            <span className="text-sm text-text-tertiary">
              Loading funnel...
            </span>
          </div>
        ) : (
          <FunnelChart stages={data.pipeline} />
        )}

        <PipelineViz stages={data.pipeline} />
      </div>

      {/* Conversion Metrics */}
      {pipeline.data && (
        <ConversionMetrics conversions={pipeline.data.conversions} />
      )}

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

      {/* Territory Breakdown */}
      {pipeline.data && (
        <TerritoryBreakdown territories={pipeline.data.territories} />
      )}

      {/* Leads Table */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-semibold text-text-heading">Leads</h2>
          <span className="text-xs text-text-tertiary">
            {data.leads.length} total
          </span>
        </div>
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
