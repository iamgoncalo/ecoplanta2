import type { AnomalyPoint } from "@/api/client.ts";
import {
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell,
} from "recharts";

interface AnomalyChartProps {
  points: AnomalyPoint[];
  totalAnomalies: number;
  affectedWorkOrders: number;
  summary?: string;
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: { payload: AnomalyPoint }[];
}

function AnomalyTooltip({ active, payload }: CustomTooltipProps) {
  if (!active || !payload?.length) return null;
  const point = payload[0].payload;
  return (
    <div className="bg-surface rounded-lg border border-border shadow-elevated px-3 py-2">
      <p className="text-xs font-semibold text-text-heading">
        {point.label ?? `Point ${point.id}`}
      </p>
      <p className="text-xs text-text-secondary">
        x: {point.x.toFixed(2)}, y: {point.y.toFixed(2)}
      </p>
      {point.work_order_id && (
        <p className="text-xs text-text-tertiary">WO: {point.work_order_id}</p>
      )}
      {point.is_anomaly && (
        <span className="inline-flex items-center mt-1 px-1.5 py-0.5 rounded text-[10px] font-semibold bg-red-50 text-red-700">
          Anomaly{point.severity ? ` - ${point.severity}` : ""}
        </span>
      )}
    </div>
  );
}

export default function AnomalyChart({
  points,
  totalAnomalies,
  affectedWorkOrders,
  summary,
}: AnomalyChartProps) {
  const normalPoints = points.filter((p) => !p.is_anomaly);
  const anomalyPoints = points.filter((p) => p.is_anomaly);

  return (
    <div className="bg-surface rounded-xl border border-border p-5 shadow-card">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-sm font-semibold text-text-heading">
            QA Anomaly Detection
          </h3>
          {summary && (
            <p className="text-xs text-text-secondary mt-0.5">{summary}</p>
          )}
        </div>
        <div className="flex items-center gap-4">
          <div className="text-right">
            <p className="text-lg font-bold text-red-600">{totalAnomalies}</p>
            <p className="text-[10px] text-text-tertiary uppercase tracking-wider">
              Anomalies
            </p>
          </div>
          <div className="text-right">
            <p className="text-lg font-bold text-text-heading">
              {affectedWorkOrders}
            </p>
            <p className="text-[10px] text-text-tertiary uppercase tracking-wider">
              Affected WOs
            </p>
          </div>
        </div>
      </div>

      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis
              dataKey="x"
              type="number"
              tick={{ fontSize: 11, fill: "#94a3b8" }}
              axisLine={false}
              tickLine={false}
              name="X"
            />
            <YAxis
              dataKey="y"
              type="number"
              tick={{ fontSize: 11, fill: "#94a3b8" }}
              axisLine={false}
              tickLine={false}
              name="Y"
            />
            <Tooltip content={<AnomalyTooltip />} />

            {/* Normal points */}
            <Scatter name="Normal" data={normalPoints}>
              {normalPoints.map((point) => (
                <Cell
                  key={point.id}
                  fill="#2563eb"
                  fillOpacity={0.5}
                  r={4}
                />
              ))}
            </Scatter>

            {/* Anomaly points - highlighted */}
            <Scatter name="Anomaly" data={anomalyPoints}>
              {anomalyPoints.map((point) => (
                <Cell
                  key={point.id}
                  fill="#ef4444"
                  fillOpacity={0.8}
                  r={7}
                  stroke="#ef4444"
                  strokeWidth={2}
                />
              ))}
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
      </div>

      {/* Legend */}
      <div className="flex items-center gap-4 mt-3 justify-center">
        <span className="flex items-center gap-1.5 text-xs text-text-secondary">
          <span className="w-2.5 h-2.5 rounded-full bg-blue-500 opacity-50" />
          Normal
        </span>
        <span className="flex items-center gap-1.5 text-xs text-text-secondary">
          <span className="w-2.5 h-2.5 rounded-full bg-red-500 ring-2 ring-red-200" />
          Anomaly
        </span>
      </div>
    </div>
  );
}
