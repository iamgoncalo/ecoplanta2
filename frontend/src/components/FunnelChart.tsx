import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell,
} from "recharts";

interface FunnelStage {
  name: string;
  count: number;
  value: number;
}

interface FunnelChartProps {
  stages: FunnelStage[];
}

const STAGE_COLORS = ["#2563eb", "#3b82f6", "#60a5fa", "#93c5fd", "#bfdbfe"];

function formatCurrency(value: number): string {
  if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(1)}M`;
  if (value >= 1_000) return `$${(value / 1_000).toFixed(0)}K`;
  return `$${value}`;
}

export default function FunnelChart({ stages }: FunnelChartProps) {
  const data = stages.map((s) => ({
    name: s.name,
    count: s.count,
    value: s.value,
  }));

  return (
    <div className="bg-surface rounded-xl border border-border p-5 shadow-card">
      <h3 className="text-sm font-semibold text-text-heading mb-4">
        Pipeline Funnel
      </h3>
      <div className="h-56">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            layout="vertical"
            margin={{ top: 0, right: 40, left: 0, bottom: 0 }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="#f1f5f9"
              horizontal={false}
            />
            <XAxis
              type="number"
              tick={{ fontSize: 11, fill: "#94a3b8" }}
              axisLine={false}
              tickLine={false}
              tickFormatter={(v: number) => formatCurrency(v)}
            />
            <YAxis
              type="category"
              dataKey="name"
              tick={{ fontSize: 11, fill: "#64748b", fontWeight: 500 }}
              axisLine={false}
              tickLine={false}
              width={90}
            />
            <Tooltip
              contentStyle={{
                borderRadius: "8px",
                border: "1px solid #e2e8f0",
                boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.05)",
                fontSize: "12px",
              }}
              formatter={(value) => [
                formatCurrency(value as number),
                "Value",
              ]}
            />
            <Bar dataKey="value" radius={[0, 6, 6, 0]} barSize={28}>
              {data.map((_, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={STAGE_COLORS[index % STAGE_COLORS.length]}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div className="flex items-center justify-center gap-4 mt-3">
        {stages.map((s, i) => (
          <div key={s.name} className="flex items-center gap-1.5">
            <div
              className="w-2.5 h-2.5 rounded-full"
              style={{
                backgroundColor: STAGE_COLORS[i % STAGE_COLORS.length],
              }}
            />
            <span className="text-[10px] text-text-secondary font-medium">
              {s.name} ({s.count})
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
