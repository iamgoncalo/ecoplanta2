import { useQuery } from "@tanstack/react-query";
import { fetchIntelligence } from "@/api/client.ts";
import type { InsightReport } from "@/api/client.ts";
import MetricCard from "@/components/MetricCard.tsx";
import StatusBadge from "@/components/StatusBadge.tsx";
import LoadingState from "@/components/LoadingState.tsx";
import ErrorState from "@/components/ErrorState.tsx";
import { FileText, Calendar } from "lucide-react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";

export default function Intelligence() {
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["intelligence"],
    queryFn: fetchIntelligence,
  });

  if (isLoading) return <LoadingState />;
  if (isError)
    return (
      <ErrorState
        message="Failed to load Intelligence data."
        onRetry={() => refetch()}
      />
    );
  if (!data) return null;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-text-heading">Intelligence</h1>
        <p className="text-sm text-text-secondary mt-0.5">
          Insights, forecasting, and key performance indicators
        </p>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {data.kpis.map((kpi) => (
          <MetricCard
            key={kpi.name}
            title={kpi.name}
            value={kpi.value}
            unit={kpi.unit}
            change={kpi.change}
            trend={kpi.trend}
          />
        ))}
      </div>

      {/* Forecasting Chart */}
      <div className="bg-surface rounded-xl border border-border p-5 shadow-card">
        <h3 className="text-sm font-semibold text-text-heading mb-4">
          Forecast vs Actual
        </h3>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data.forecasts}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis
                dataKey="period"
                tick={{ fontSize: 11, fill: "#94a3b8" }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                tick={{ fontSize: 11, fill: "#94a3b8" }}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip
                contentStyle={{
                  borderRadius: "8px",
                  border: "1px solid #e2e8f0",
                  boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.05)",
                  fontSize: "12px",
                }}
              />
              <Legend
                wrapperStyle={{ fontSize: "11px", paddingTop: "8px" }}
              />
              <Line
                type="monotone"
                dataKey="actual"
                stroke="#2563eb"
                strokeWidth={2}
                dot={{ r: 3, fill: "#2563eb" }}
                name="Actual"
                connectNulls={false}
              />
              <Line
                type="monotone"
                dataKey="forecast"
                stroke="#94a3b8"
                strokeWidth={2}
                strokeDasharray="6 3"
                dot={{ r: 3, fill: "#94a3b8" }}
                name="Forecast"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Insight Reports */}
      <div>
        <h2 className="text-sm font-semibold text-text-heading mb-3">
          Insight Reports
        </h2>
        <div className="space-y-3">
          {data.insights.length === 0 ? (
            <div className="bg-surface rounded-xl border border-border p-12 text-center">
              <p className="text-sm text-text-tertiary">No insight reports available</p>
            </div>
          ) : (
            data.insights.map((insight: InsightReport) => (
              <div
                key={insight.id}
                className="bg-surface rounded-xl border border-border p-5 shadow-card hover:shadow-elevated transition-shadow"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded-lg bg-eco-50 flex items-center justify-center flex-shrink-0 mt-0.5">
                      <FileText size={14} className="text-eco-600" />
                    </div>
                    <div>
                      <h4 className="text-sm font-semibold text-text-heading">
                        {insight.title}
                      </h4>
                      <div className="flex items-center gap-2 mt-1">
                        <StatusBadge label={insight.category} />
                        <StatusBadge label={insight.impact} />
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-1.5 text-xs text-text-tertiary flex-shrink-0">
                    <Calendar size={12} />
                    {insight.date}
                  </div>
                </div>
                <p className="text-xs text-text-secondary mt-2 ml-11">
                  {insight.summary}
                </p>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
