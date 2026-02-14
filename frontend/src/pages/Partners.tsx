import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import {
  fetchPartners,
  runOptimization,
  fetchCompliance,
} from "@/api/client.ts";
import type {
  Partner,
  OptimizationResult,
  ComplianceRecord,
} from "@/api/client.ts";
import MetricCard from "@/components/MetricCard.tsx";
import StatusBadge from "@/components/StatusBadge.tsx";
import PartnerCard from "@/components/PartnerCard.tsx";
import AllocationView from "@/components/AllocationView.tsx";
import LoadingState from "@/components/LoadingState.tsx";
import ErrorState from "@/components/ErrorState.tsx";
import {
  Users,
  Globe,
  ShieldCheck,
  Star,
  Play,
  Loader2,
  CheckCircle2,
  XCircle,
  Clock,
} from "lucide-react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";

function ComplianceBadge({
  passed,
  label,
}: {
  passed: boolean;
  label: string;
}) {
  return (
    <span className="inline-flex items-center gap-1 text-xs font-medium">
      {passed ? (
        <CheckCircle2 size={12} className="text-emerald-500" />
      ) : (
        <XCircle size={12} className="text-slate-300" />
      )}
      <span className={passed ? "text-emerald-700" : "text-text-tertiary"}>
        {label}
      </span>
    </span>
  );
}

export default function Partners() {
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["partners"],
    queryFn: fetchPartners,
  });

  const { data: complianceData } = useQuery({
    queryKey: ["compliance"],
    queryFn: fetchCompliance,
  });

  const [optimizationResult, setOptimizationResult] =
    useState<OptimizationResult | null>(null);

  const optimizeMutation = useMutation({
    mutationFn: runOptimization,
    onSuccess: (result) => {
      setOptimizationResult(result);
    },
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

  // Group partners by country/region for the "EU Map" view
  const partnersByCountry = data.partners.reduce<Record<string, Partner[]>>(
    (acc, p) => {
      const key = p.country ?? p.region;
      if (!acc[key]) acc[key] = [];
      acc[key].push(p);
      return acc;
    },
    {},
  );

  const complianceRecords: ComplianceRecord[] =
    complianceData?.records ?? [];

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

      {/* Partner Network - Grouped by Country */}
      <div>
        <h2 className="text-sm font-semibold text-text-heading mb-3">
          Partner Network
        </h2>
        {data.partners.length === 0 ? (
          <div className="bg-surface rounded-xl border border-border p-12 text-center">
            <p className="text-sm text-text-tertiary">
              No partners registered
            </p>
          </div>
        ) : (
          <div className="space-y-6">
            {Object.entries(partnersByCountry).map(([country, partners]) => (
              <div key={country}>
                <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-3 flex items-center gap-2">
                  <Globe size={12} />
                  {country}{" "}
                  <span className="text-text-tertiary font-normal">
                    ({partners.length})
                  </span>
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {partners.map((partner: Partner) => (
                    <PartnerCard key={partner.id} partner={partner} />
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Allocation Panel */}
      <div className="bg-surface rounded-xl border border-border p-5 shadow-card">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-semibold text-text-heading">
              Order Allocation Optimization
            </h3>
            <p className="text-xs text-text-secondary mt-0.5">
              Run the optimization engine to distribute orders across the
              partner network
            </p>
          </div>
          <button
            onClick={() => optimizeMutation.mutate()}
            disabled={optimizeMutation.isPending}
            className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-eco-600 hover:bg-eco-700 disabled:opacity-60 rounded-lg transition-colors shadow-sm"
          >
            {optimizeMutation.isPending ? (
              <Loader2 size={14} className="animate-spin" />
            ) : (
              <Play size={14} />
            )}
            {optimizeMutation.isPending
              ? "Optimizing..."
              : "Run Optimization"}
          </button>
        </div>

        {optimizeMutation.isError && (
          <div className="bg-red-50 text-red-700 rounded-lg px-4 py-2.5 text-xs font-medium mb-4">
            Optimization failed. Please try again.
          </div>
        )}

        {optimizationResult && (
          <AllocationView result={optimizationResult} />
        )}

        {!optimizationResult && !optimizeMutation.isPending && (
          <div className="bg-surface-secondary rounded-lg p-8 text-center">
            <p className="text-sm text-text-tertiary">
              Click &quot;Run Optimization&quot; to generate allocation
              recommendations
            </p>
          </div>
        )}
      </div>

      {/* Compliance Overview */}
      <div>
        <h2 className="text-sm font-semibold text-text-heading mb-3 flex items-center gap-2">
          <ShieldCheck size={14} className="text-eco-600" />
          Compliance Overview
        </h2>
        {complianceRecords.length === 0 ? (
          <div className="bg-surface rounded-xl border border-border p-5 shadow-card">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border bg-surface-secondary">
                    <th className="px-4 py-3 text-left text-xs font-semibold text-text-secondary uppercase tracking-wider">
                      Partner
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-text-secondary uppercase tracking-wider">
                      Status
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {data.partners.map((p: Partner) => (
                    <tr
                      key={p.id}
                      className="border-b border-border-light last:border-b-0"
                    >
                      <td className="px-4 py-3 text-text-primary font-medium">
                        {p.name}
                      </td>
                      <td className="px-4 py-3">
                        <StatusBadge label={p.compliance_status} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <div className="bg-surface rounded-xl border border-border shadow-card overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border bg-surface-secondary">
                    <th className="px-4 py-3 text-left text-xs font-semibold text-text-secondary uppercase tracking-wider">
                      Partner
                    </th>
                    <th className="px-4 py-3 text-center text-xs font-semibold text-text-secondary uppercase tracking-wider">
                      CE Mark
                    </th>
                    <th className="px-4 py-3 text-center text-xs font-semibold text-text-secondary uppercase tracking-wider">
                      ISO 9001
                    </th>
                    <th className="px-4 py-3 text-center text-xs font-semibold text-text-secondary uppercase tracking-wider">
                      ISO 14001
                    </th>
                    <th className="px-4 py-3 text-center text-xs font-semibold text-text-secondary uppercase tracking-wider">
                      EN 1090
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-text-secondary uppercase tracking-wider">
                      Last Audit
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {complianceRecords.map((rec) => (
                    <tr
                      key={rec.partner_id}
                      className="border-b border-border-light last:border-b-0 hover:bg-surface-secondary transition-colors"
                    >
                      <td className="px-4 py-3 text-text-primary font-medium">
                        {rec.partner_name}
                      </td>
                      <td className="px-4 py-3 text-center">
                        <ComplianceBadge
                          passed={rec.ce_mark}
                          label="CE"
                        />
                      </td>
                      <td className="px-4 py-3 text-center">
                        <ComplianceBadge
                          passed={rec.iso_9001}
                          label="9001"
                        />
                      </td>
                      <td className="px-4 py-3 text-center">
                        <ComplianceBadge
                          passed={rec.iso_14001}
                          label="14001"
                        />
                      </td>
                      <td className="px-4 py-3 text-center">
                        <ComplianceBadge
                          passed={rec.en_1090}
                          label="1090"
                        />
                      </td>
                      <td className="px-4 py-3 text-xs text-text-secondary">
                        {rec.last_audit ? (
                          <span className="flex items-center gap-1">
                            <Clock size={10} />
                            {rec.last_audit}
                          </span>
                        ) : (
                          "--"
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
