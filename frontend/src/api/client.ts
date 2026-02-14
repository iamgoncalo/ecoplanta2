const BASE_URL =
  import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${BASE_URL}${path}`;
  const res = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  if (!res.ok) {
    const body = await res.text().catch(() => "Unknown error");
    throw new ApiError(res.status, body);
  }

  return res.json() as Promise<T>;
}

/* ---- Health ---- */

export interface HealthResponse {
  status: string;
  version?: string;
  uptime?: number;
}

export function fetchHealth(): Promise<HealthResponse> {
  return request<HealthResponse>("/health");
}

/* ---- Fabric ---- */

export interface ProductionLine {
  id: string;
  name: string;
  status: string;
  throughput: number;
  efficiency: number;
  product: string;
}

export interface WorkOrder {
  id: string;
  product: string;
  quantity: number;
  status: string;
  due_date: string;
  priority: string;
}

export interface FabricResponse {
  production_lines: ProductionLine[];
  work_orders: WorkOrder[];
  metrics: Record<string, number>;
}

export function fetchFabric(): Promise<FabricResponse> {
  return request<FabricResponse>("/api/fabric");
}

/* ---- Factory (extended) ---- */

export interface BomItem {
  material: string;
  quantity: number;
  unit: string;
  unit_cost: number;
}

export interface QARecord {
  id: string;
  work_order_id: string;
  inspector: string;
  result: string;
  defects: string[];
  date: string;
}

export interface WorkOrderDetail extends WorkOrder {
  bom: BomItem[];
  qa_records: QARecord[];
}

export function fetchWorkOrders(): Promise<{ work_orders: WorkOrder[] }> {
  return request<{ work_orders: WorkOrder[] }>("/api/factory/workorders");
}

export function fetchWorkOrder(id: string): Promise<WorkOrderDetail> {
  return request<WorkOrderDetail>(`/api/factory/workorders/${id}`);
}

export interface InventoryItem {
  id: string;
  material: string;
  quantity: number;
  unit: string;
  reorder_level: number;
  status: string;
}

export interface InventoryResponse {
  items: InventoryItem[];
  alerts: { material: string; message: string; severity: string }[];
}

export function fetchInventory(): Promise<InventoryResponse> {
  return request<InventoryResponse>("/api/factory/inventory");
}

export interface QAResponse {
  records: QARecord[];
  summary: {
    total_inspections: number;
    pass_rate: number;
    common_defects: { defect: string; count: number }[];
  };
}

export function fetchQARecords(): Promise<QAResponse> {
  return request<QAResponse>("/api/factory/qa");
}

/* ---- Fabric Scene ---- */

export interface SceneObject {
  id: string;
  type: string;
  name: string;
  position: [number, number, number];
  scale: [number, number, number];
  color: string;
  metadata?: Record<string, unknown>;
}

export interface FabricSceneResponse {
  objects: SceneObject[];
}

export function fetchFabricScene(): Promise<FabricSceneResponse> {
  return request<FabricSceneResponse>("/api/fabric/scene");
}

/* ---- Frameworks ---- */

export interface Framework {
  id: string;
  name: string;
  type: string;
  structural_rating: number;
  material: string;
  smart_enabled: boolean;
  description: string;
}

export interface Material {
  id: string;
  name: string;
  category: string;
  grade: string;
  properties: Record<string, unknown>;
}

export interface Patent {
  id: string;
  title: string;
  filing_date: string;
  status: string;
  description: string;
}

export interface FrameworksResponse {
  frameworks: Framework[];
  materials: Material[];
  patents: Patent[];
}

export function fetchFrameworks(): Promise<FrameworksResponse> {
  return request<FrameworksResponse>("/api/frameworks");
}

/* ---- Sales ---- */

export interface PipelineStage {
  name: string;
  count: number;
  value: number;
}

export interface Lead {
  id: string;
  company: string;
  contact: string;
  score: number;
  stage: string;
  value: number;
  last_activity: string;
}

export interface SalesMetrics {
  total_revenue: number;
  conversion_rate: number;
  avg_deal_size: number;
  pipeline_value: number;
}

export interface RevenueDataPoint {
  month: string;
  revenue: number;
  target: number;
}

export interface SalesResponse {
  pipeline: PipelineStage[];
  leads: Lead[];
  metrics: SalesMetrics;
  revenue_chart: RevenueDataPoint[];
}

export function fetchSales(): Promise<SalesResponse> {
  return request<SalesResponse>("/api/sales");
}

export interface PipelineStats {
  stages: PipelineStage[];
  conversions: { from: string; to: string; rate: number }[];
  territories: {
    region: string;
    lead_count: number;
    value: number;
  }[];
}

export function fetchSalesPipeline(): Promise<PipelineStats> {
  return request<PipelineStats>("/api/sales/pipeline/stats");
}

export interface CreateLeadPayload {
  company: string;
  contact: string;
  value: number;
  stage?: string;
}

export function createLead(data: CreateLeadPayload): Promise<Lead> {
  return request<Lead>("/api/sales/leads", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function updateLeadStage(
  id: string,
  stage: string,
): Promise<Lead> {
  return request<Lead>(`/api/sales/leads/${id}`, {
    method: "PATCH",
    body: JSON.stringify({ stage }),
  });
}

/* ---- Intelligence ---- */

export interface InsightReport {
  id: string;
  title: string;
  category: string;
  summary: string;
  date: string;
  impact: string;
}

export interface ForecastDataPoint {
  period: string;
  actual: number | null;
  forecast: number;
}

export interface KpiMetric {
  name: string;
  value: number;
  unit: string;
  change: number;
  trend: string;
}

export interface IntelligenceResponse {
  insights: InsightReport[];
  forecasts: ForecastDataPoint[];
  kpis: KpiMetric[];
}

export function fetchIntelligence(): Promise<IntelligenceResponse> {
  return request<IntelligenceResponse>("/api/intelligence");
}

/* ---- Deploy ---- */

export interface Delivery {
  id: string;
  destination: string;
  status: string;
  eta: string;
  progress: number;
  items: number;
}

export interface DeployJob {
  id: string;
  site: string;
  type: string;
  status: string;
  started: string;
  team: string;
}

export interface DeployResponse {
  deliveries: Delivery[];
  jobs: DeployJob[];
  metrics: Record<string, number>;
}

export function fetchDeploy(): Promise<DeployResponse> {
  return request<DeployResponse>("/api/deploy");
}

export interface ScheduledDelivery {
  id: string;
  date: string;
  destination: string;
  items: number;
  status: string;
}

export interface DeliveryScheduleResponse {
  scheduled: ScheduledDelivery[];
}

export function fetchDeliverySchedule(): Promise<DeliveryScheduleResponse> {
  return request<DeliveryScheduleResponse>("/api/deploy/schedule");
}

export interface ChecklistItem {
  id: string;
  label: string;
  completed: boolean;
}

export interface CommissioningJob {
  id: string;
  site: string;
  status: string;
  started: string;
  checklist: ChecklistItem[];
  progress: number;
}

export interface CommissioningResponse {
  jobs: CommissioningJob[];
  summary: {
    total: number;
    pending: number;
    in_progress: number;
    completed: number;
  };
}

export function fetchCommissioning(): Promise<CommissioningResponse> {
  return request<CommissioningResponse>("/api/deploy/commissioning");
}

/* ---- Partners ---- */

export interface Partner {
  id: string;
  name: string;
  type: string;
  region: string;
  capacity_utilization: number;
  compliance_status: string;
  active_projects: number;
  rating: number;
}

export interface PartnersResponse {
  partners: Partner[];
  metrics: Record<string, number>;
}

export function fetchPartners(): Promise<PartnersResponse> {
  return request<PartnersResponse>("/api/partners");
}

/* ---- User ---- */

export interface UserProfile {
  id: string;
  name: string;
  email: string;
  role: string;
}

export function fetchMe(): Promise<UserProfile> {
  return request<UserProfile>("/api/me");
}
