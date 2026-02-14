import type { ForecastDataPoint } from "@/api/client.ts";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";

interface ForecastChartProps {
  data: ForecastDataPoint[];
  title?: string;
  confidence?: number;
}

export default function ForecastChart({
  data,
  title = "Lead Time Forecast",
  confidence,
}: ForecastChartProps) {
  return (
    <div className="bg-surface rounded-xl border border-border p-5 shadow-card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-text-heading">{title}</h3>
        {confidence != null && (
          <span className="text-xs text-text-tertiary">
            Confidence: {(confidence * 100).toFixed(0)}%
          </span>
        )}
      </div>
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data}>
            <defs>
              <linearGradient id="forecastGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#94a3b8" stopOpacity={0.15} />
                <stop offset="95%" stopColor="#94a3b8" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="actualGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#2563eb" stopOpacity={0.2} />
                <stop offset="95%" stopColor="#2563eb" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="confidenceGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#a78bfa" stopOpacity={0.1} />
                <stop offset="95%" stopColor="#a78bfa" stopOpacity={0.02} />
              </linearGradient>
            </defs>
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

            {/* Confidence interval band */}
            <Area
              type="monotone"
              dataKey="upper_bound"
              stroke="none"
              fill="url(#confidenceGrad)"
              name="Upper Bound"
              dot={false}
              activeDot={false}
            />
            <Area
              type="monotone"
              dataKey="lower_bound"
              stroke="none"
              fill="url(#confidenceGrad)"
              name="Lower Bound"
              dot={false}
              activeDot={false}
            />

            {/* Forecast area */}
            <Area
              type="monotone"
              dataKey="forecast"
              stroke="#94a3b8"
              strokeWidth={2}
              strokeDasharray="6 3"
              fill="url(#forecastGrad)"
              dot={{ r: 3, fill: "#94a3b8" }}
              name="Forecast"
            />

            {/* Actual line on top */}
            <Line
              type="monotone"
              dataKey="actual"
              stroke="#2563eb"
              strokeWidth={2}
              dot={{ r: 3, fill: "#2563eb" }}
              name="Actual"
              connectNulls={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
