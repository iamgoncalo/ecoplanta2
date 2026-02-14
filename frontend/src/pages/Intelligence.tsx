import { useQuery, useMutation } from "@tanstack/react-query";
import {
  fetchIntelligence,
  fetchModels,
  runForecast,
  detectAnomalies,
  fetchFeatureStore,
} from "@/api/client.ts";
import type {
  InsightReport,
  LeadTimeForecast,
  AnomalyDetectionResult,
} from "@/api/client.ts";
import MetricCard from "@/components/MetricCard.tsx";
import StatusBadge from "@/components/StatusBadge.tsx";
import ModelCard from "@/components/ModelCard.tsx";
import ForecastChart from "@/components/ForecastChart.tsx";
import AnomalyChart from "@/components/AnomalyChart.tsx";
import LoadingState from "@/components/LoadingState.tsx";
import ErrorState from "@/components/ErrorState.tsx";
import {
  FileText,
  Calendar,
  Brain,
  Play,
  Loader2,
  Database,
} from "lucide-react";

export default function Intelligence() {
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["intelligence"],
    queryFn: fetchIntelligence,
  });

  const { data: modelsData } = useQuery({
    queryKey: ["intelligence-models"],
    queryFn: fetchModels,
  });

  const { data: featureStoreData } = useQuery({
    queryKey: ["feature-store"],
    queryFn: fetchFeatureStore,
  });

  const forecastMutation = useMutation({
    mutationFn: runForecast,
  });

  const anomalyMutation = useMutation({
    mutationFn: detectAnomalies,
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

  const models = modelsData?.models ?? [];
  const features = featureStoreData?.features ?? [];
  const forecastResult: LeadTimeForecast | undefined =
    forecastMutation.data ?? undefined;
  const anomalyResult: AnomalyDetectionResult | undefined =
    anomalyMutation.data ?? undefined;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-text-heading">Intelligence</h1>
        <p className="text-sm text-text-secondary mt-0.5">
          AI/ML dashboard, forecasting, anomaly detection, and insights
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

      {/* Models Overview */}
      {models.length > 0 && (
        <div>
          <h2 className="text-sm font-semibold text-text-heading mb-3 flex items-center gap-2">
            <Brain size={14} className="text-violet-600" />
            ML Models
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {models.map((model) => (
              <ModelCard key={model.id} model={model} />
            ))}
          </div>
        </div>
      )}

      {/* Lead Time Forecast */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-semibold text-text-heading flex items-center gap-2">
            Lead Time Forecast
          </h2>
          <button
            onClick={() => forecastMutation.mutate()}
            disabled={forecastMutation.isPending}
            className="inline-flex items-center gap-2 px-3 py-1.5 text-xs font-medium text-white bg-eco-600 hover:bg-eco-700 disabled:opacity-60 rounded-lg transition-colors shadow-sm"
          >
            {forecastMutation.isPending ? (
              <Loader2 size={12} className="animate-spin" />
            ) : (
              <Play size={12} />
            )}
            {forecastMutation.isPending ? "Running..." : "Run Forecast"}
          </button>
        </div>

        {forecastMutation.isError && (
          <div className="bg-red-50 text-red-700 rounded-lg px-4 py-2.5 text-xs font-medium mb-4">
            Forecast failed. Please try again.
          </div>
        )}

        {forecastResult ? (
          <ForecastChart
            data={forecastResult.data_points}
            title={
              forecastResult.model_name
                ? `Lead Time Forecast (${forecastResult.model_name})`
                : "Lead Time Forecast"
            }
            confidence={forecastResult.confidence_level}
          />
        ) : (
          <ForecastChart
            data={data.forecasts}
            title="Forecast vs Actual"
          />
        )}
      </div>

      {/* QA Anomaly Detection */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-semibold text-text-heading flex items-center gap-2">
            QA Anomaly Detection
          </h2>
          <button
            onClick={() => anomalyMutation.mutate()}
            disabled={anomalyMutation.isPending}
            className="inline-flex items-center gap-2 px-3 py-1.5 text-xs font-medium text-white bg-violet-600 hover:bg-violet-700 disabled:opacity-60 rounded-lg transition-colors shadow-sm"
          >
            {anomalyMutation.isPending ? (
              <Loader2 size={12} className="animate-spin" />
            ) : (
              <Play size={12} />
            )}
            {anomalyMutation.isPending ? "Detecting..." : "Detect Anomalies"}
          </button>
        </div>

        {anomalyMutation.isError && (
          <div className="bg-red-50 text-red-700 rounded-lg px-4 py-2.5 text-xs font-medium mb-4">
            Anomaly detection failed. Please try again.
          </div>
        )}

        {anomalyResult ? (
          <AnomalyChart
            points={anomalyResult.points}
            totalAnomalies={anomalyResult.total_anomalies}
            affectedWorkOrders={anomalyResult.affected_work_orders}
            summary={anomalyResult.summary}
          />
        ) : (
          <div className="bg-surface rounded-xl border border-border p-8 text-center shadow-card">
            <p className="text-sm text-text-tertiary">
              Click &quot;Detect Anomalies&quot; to run QA anomaly detection
            </p>
          </div>
        )}
      </div>

      {/* Feature Store */}
      {features.length > 0 && (
        <div>
          <h2 className="text-sm font-semibold text-text-heading mb-3 flex items-center gap-2">
            <Database size={14} className="text-blue-600" />
            Feature Store
          </h2>
          <div className="bg-surface rounded-xl border border-border shadow-card overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border bg-surface-secondary">
                    <th className="px-4 py-3 text-left text-xs font-semibold text-text-secondary uppercase tracking-wider">
                      Feature
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-text-secondary uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-text-secondary uppercase tracking-wider">
                      Description
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-text-secondary uppercase tracking-wider">
                      Source
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {features.map((feat) => (
                    <tr
                      key={feat.name}
                      className="border-b border-border-light last:border-b-0 hover:bg-surface-secondary transition-colors"
                    >
                      <td className="px-4 py-3 text-text-primary font-medium">
                        {feat.name}
                      </td>
                      <td className="px-4 py-3">
                        <StatusBadge label={feat.type} variant="info" />
                      </td>
                      <td className="px-4 py-3 text-text-secondary text-xs">
                        {feat.description}
                      </td>
                      <td className="px-4 py-3 text-text-tertiary text-xs">
                        {feat.source ?? "--"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Insight Reports Feed */}
      <div>
        <h2 className="text-sm font-semibold text-text-heading mb-3">
          Insights Feed
        </h2>
        <div className="space-y-3">
          {data.insights.length === 0 ? (
            <div className="bg-surface rounded-xl border border-border p-12 text-center">
              <p className="text-sm text-text-tertiary">
                No insight reports available
              </p>
            </div>
          ) : (
            <div className="relative">
              {/* Timeline line */}
              <div className="absolute left-[18px] top-0 bottom-0 w-px bg-border" />

              {data.insights.map((insight: InsightReport, idx: number) => (
                <div
                  key={insight.id}
                  className="relative pl-11 pb-4 last:pb-0"
                >
                  {/* Timeline dot */}
                  <div className="absolute left-[14px] top-5 w-2.5 h-2.5 rounded-full bg-eco-500 ring-4 ring-surface z-10" />

                  <div className="bg-surface rounded-xl border border-border p-5 shadow-card hover:shadow-elevated transition-shadow">
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
                    {idx === 0 && (
                      <div className="ml-11 mt-2">
                        <span className="inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-semibold bg-eco-50 text-eco-700 ring-1 ring-inset ring-eco-600/10">
                          Latest
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
