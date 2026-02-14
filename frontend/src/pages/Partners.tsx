import { useQuery } from "@tanstack/react-query";
import { fetchPartners } from "@/api/client.ts";
import type { Partner } from "@/api/client.ts";
import MetricCard from "@/components/MetricCard.tsx";
import StatusBadge from "@/components/StatusBadge.tsx";
import LoadingState from "@/components/LoadingState.tsx";
import ErrorState from "@/components/ErrorState.tsx";
import { Users, Globe, ShieldCheck, Star } from "lucide-react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";
import clsx from "clsx";

function RatingStars({ rating, max = 5 }: { rating: number; max?: number }) {
  return (
    <div className="flex items-center gap-0.5">
      {Array.from({ length: max }).map((_, i) => (
        <Star
          key={i}
          size={12}
          className={clsx(
            i < rating ? "text-amber-400 fill-amber-400" : "text-slate-200",
          )}
        />
      ))}
    </div>
  );
}

export default function Partners() {
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["partners"],
    queryFn: fetchPartners,
  });

  if (isLoading) return <LoadingState />;
  if (isError)
    return (
      <ErrorState
        message="Failed to load Partners data."
        onRetry={() => refetch()}
      />
    );
  if (!data) return null;

  const metrics = data.metrics ?? {};

  const capacityChartData = data.partners.map((p: Partner) => ({
    name: p.name.length > 12 ? p.name.slice(0, 12) + "..." : p.name,
    utilization: p.capacity_utilization,
  }));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-text-heading">Partners</h1>
        <p className="text-sm text-text-secondary mt-0.5">
          Partner network, capacity monitoring, and compliance tracking
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Partners"
          value={metrics.total_partners ?? data.partners.length}
          icon={Users}
        />
        <MetricCard
          title="Regions"
          value={metrics.regions ?? 0}
          icon={Globe}
        />
        <MetricCard
          title="Compliant"
          value={metrics.compliant ?? 0}
          icon={ShieldCheck}
          trend="up"
        />
        <MetricCard
          title="Avg Utilization"
          value={`${metrics.avg_utilization ?? 0}%`}
          icon={Star}
        />
      </div>

      {/* Capacity Utilization Chart */}
      <div className="bg-surface rounded-xl border border-border p-5 shadow-card">
        <h3 className="text-sm font-semibold text-text-heading mb-4">
          Capacity Utilization by Partner
        </h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={capacityChartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis
                dataKey="name"
                tick={{ fontSize: 10, fill: "#94a3b8" }}
                axisLine={false}
                tickLine={false}
                angle={-30}
                textAnchor="end"
                height={50}
              />
              <YAxis
                tick={{ fontSize: 11, fill: "#94a3b8" }}
                axisLine={false}
                tickLine={false}
                domain={[0, 100]}
                tickFormatter={(v: number) => `${v}%`}
              />
              <Tooltip
                contentStyle={{
                  borderRadius: "8px",
                  border: "1px solid #e2e8f0",
                  boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.05)",
                  fontSize: "12px",
                }}
                formatter={(value) => [`${value}%`, "Utilization"]}
              />
              <Bar
                dataKey="utilization"
                fill="#2563eb"
                radius={[4, 4, 0, 0]}
                maxBarSize={40}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Partner Grid */}
      <div>
        <h2 className="text-sm font-semibold text-text-heading mb-3">
          Partner Network
        </h2>
        {data.partners.length === 0 ? (
          <div className="bg-surface rounded-xl border border-border p-12 text-center">
            <p className="text-sm text-text-tertiary">No partners registered</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {data.partners.map((partner: Partner) => (
              <div
                key={partner.id}
                className="bg-surface rounded-xl border border-border p-5 shadow-card hover:shadow-elevated transition-shadow"
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="text-sm font-semibold text-text-heading">
                      {partner.name}
                    </h3>
                    <span className="text-xs text-text-tertiary">
                      {partner.type} &middot; {partner.region}
                    </span>
                  </div>
                  <StatusBadge label={partner.compliance_status} />
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-text-secondary">
                      Capacity
                    </span>
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-1.5 bg-surface-tertiary rounded-full overflow-hidden">
                        <div
                          className={clsx(
                            "h-full rounded-full",
                            partner.capacity_utilization >= 80
                              ? "bg-danger"
                              : partner.capacity_utilization >= 50
                                ? "bg-warning"
                                : "bg-success",
                          )}
                          style={{
                            width: `${partner.capacity_utilization}%`,
                          }}
                        />
                      </div>
                      <span className="text-xs text-text-secondary font-medium">
                        {partner.capacity_utilization}%
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-xs text-text-secondary">
                      Active Projects
                    </span>
                    <span className="text-xs font-medium text-text-primary">
                      {partner.active_projects}
                    </span>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-xs text-text-secondary">Rating</span>
                    <RatingStars rating={partner.rating} />
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
