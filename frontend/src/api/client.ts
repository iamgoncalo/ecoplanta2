const API_BASE_URL =
  import.meta.env.VITE_API_URL ?? "http://localhost:8000";

// Static JSON base path — uses Vite's base URL for correct asset resolution
const STATIC_BASE = import.meta.env.BASE_URL + "api";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

// Map API paths to static JSON file names for fallback
const STATIC_FILE_MAP: Record<string, string> = {
  "/health": "health.json",
  "/api/fabric": "fabric.json",
  "/api/fabric/scene": "fabric-scene.json",
  "/api/frameworks": "frameworks.json",
  "/api/sales": "sales.json",
  "/api/intelligence": "intelligence.json",
  "/api/deploy": "deploy.json",
  "/api/partners": "partners.json",
};

let _backendOnline: boolean | null = null;

export function isBackendOnline(): boolean | null {
  return _backendOnline;
}

async function tryStaticFallback<T>(path: string): Promise<T | null> {
  const staticFile = STATIC_FILE_MAP[path];
  if (!staticFile) return null;
  try {
    const res = await fetch(`${STATIC_BASE}/${staticFile}`);
    if (res.ok) return (await res.json()) as T;
  } catch {
    // Static file also not available
  }
  return null;
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  // For mutating requests (POST/PATCH/PUT/DELETE), never use static fallback
  const isMutating = options?.method && options.method !== "GET";

  try {
    const url = `${API_BASE_URL}${path}`;
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 5000);

    const res = await fetch(url, {
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
      signal: controller.signal,
      ...options,
    });
    clearTimeout(timeout);

    if (!res.ok) {
      throw new ApiError(res.status, await res.text().catch(() => "Unknown error"));
    }

    _backendOnline = true;
    return (await res.json()) as T;
  } catch (err) {
    _backendOnline = false;

    // For GET requests, try static fallback
    if (!isMutating) {
      const fallback = await tryStaticFallback<T>(path);
      if (fallback !== null) return fallback;
    }

    throw err;
  }
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
  strength?: number;
  thermal_conductivity?: number;
  embodied_carbon?: number;
  is_smart?: boolean;
}

export interface MaterialDetail extends Material {
  description?: string;
  applications?: string[];
  certifications?: string[];
}

export interface MaterialComparison {
  materials: MaterialDetail[];
  comparison_fields: string[];
}

export interface Patent {
  id: string;
  title: string;
  filing_date: string;
  status: string;
  description: string;
}

export interface PatentDetail extends Patent {
  claims_summary?: string;
  experiment_results?: string;
  novelty_notes?: string;
  inventors?: string[];
}

export interface FrameworksResponse {
  frameworks: Framework[];
  materials: Material[];
  patents: Patent[];
}

export function fetchFrameworks(): Promise<FrameworksResponse> {
  return request<FrameworksResponse>("/api/frameworks");
}

export interface MaterialFilters {
  category?: string;
  grade?: string;
  smart_only?: boolean;
  search?: string;
}

export function fetchMaterials(
  filters?: MaterialFilters,
): Promise<{ materials: Material[] }> {
  const params = new URLSearchParams();
  if (filters?.category) params.set("category", filters.category);
  if (filters?.grade) params.set("grade", filters.grade);
  if (filters?.smart_only) params.set("smart_only", "true");
  if (filters?.search) params.set("search", filters.search);
  const qs = params.toString();
  return request<{ materials: Material[] }>(
    `/api/materials${qs ? `?${qs}` : ""}`,
  );
}

export function fetchMaterialDetail(id: string): Promise<MaterialDetail> {
  return request<MaterialDetail>(`/api/materials/${id}`);
}

export function compareMaterials(
  ids: string[],
): Promise<MaterialComparison> {
  const qs = ids.map((id) => `ids=${encodeURIComponent(id)}`).join("&");
  return request<MaterialComparison>(`/api/materials/compare?${qs}`);
}

export function fetchSmartMaterials(): Promise<{ materials: Material[] }> {
  return request<{ materials: Material[] }>("/api/materials/smart");
}

export function fetchPatents(): Promise<{ patents: Patent[] }> {
  return request<{ patents: Patent[] }>("/api/patents");
}

export function fetchPatentDetail(id: string): Promise<PatentDetail> {
  return request<PatentDetail>(`/api/patents/${id}`);
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
  lower_bound?: number;
  upper_bound?: number;
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

export interface MLModel {
  id: string;
  name: string;
  type: string;
  status: string;
  accuracy?: number;
  metric_value?: number;
  metric_name?: string;
  last_trained?: string;
  description?: string;
}

export interface ModelsResponse {
  models: MLModel[];
}

export function fetchModels(): Promise<ModelsResponse> {
  return request<ModelsResponse>("/api/intelligence/models");
}

export interface LeadTimeForecast {
  data_points: ForecastDataPoint[];
  model_name?: string;
  confidence_level?: number;
}

export function runForecast(): Promise<LeadTimeForecast> {
  return request<LeadTimeForecast>("/api/intelligence/forecast", {
    method: "POST",
  });
}

export interface AnomalyPoint {
  id: string;
  x: number;
  y: number;
  is_anomaly: boolean;
  label?: string;
  work_order_id?: string;
  severity?: string;
}

export interface AnomalyDetectionResult {
  points: AnomalyPoint[];
  total_anomalies: number;
  affected_work_orders: number;
  summary?: string;
}

export function detectAnomalies(): Promise<AnomalyDetectionResult> {
  return request<AnomalyDetectionResult>("/api/intelligence/anomaly-detect", {
    method: "POST",
  });
}

export interface FeatureEntry {
  name: string;
  type: string;
  description: string;
  source?: string;
  updated?: string;
}

export interface FeatureStoreResponse {
  features: FeatureEntry[];
}

export function fetchFeatureStore(): Promise<FeatureStoreResponse> {
  return request<FeatureStoreResponse>("/api/intelligence/feature-store");
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
  country?: string;
  capacity_utilization: number;
  capacity?: number;
  compliance_status: string;
  active_projects: number;
  rating: number;
  lead_time?: number;
}

export interface PartnerDetail extends Partner {
  contact_email?: string;
  certifications?: string[];
  monthly_utilization?: { month: string; utilization: number }[];
}

export interface PartnersResponse {
  partners: Partner[];
  metrics: Record<string, number>;
}

export function fetchPartners(): Promise<PartnersResponse> {
  return request<PartnersResponse>("/api/partners");
}

export function fetchPartnerDetail(id: string): Promise<PartnerDetail> {
  return request<PartnerDetail>(`/api/partners/${id}`);
}

export interface AllocateOrderPayload {
  order_id?: string;
  product?: string;
  quantity?: number;
  requirements?: string[];
}

export interface AllocationResult {
  allocations: {
    partner_id: string;
    partner_name: string;
    quantity: number;
    reasoning: string;
    estimated_lead_time?: number;
  }[];
}

export function allocateOrder(
  data: AllocateOrderPayload,
): Promise<AllocationResult> {
  return request<AllocationResult>("/api/partners/allocate", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export interface OptimizationResult {
  allocations: {
    partner_id: string;
    partner_name: string;
    orders: string[];
    utilization: number;
    reasoning: string;
  }[];
  total_cost_savings?: number;
  optimization_score?: number;
}

export function runOptimization(): Promise<OptimizationResult> {
  return request<OptimizationResult>("/api/partners/optimize");
}

export interface ComplianceRecord {
  partner_id: string;
  partner_name: string;
  ce_mark: boolean;
  iso_9001: boolean;
  iso_14001: boolean;
  en_1090: boolean;
  last_audit?: string;
  notes?: string;
}

export interface ComplianceResponse {
  records: ComplianceRecord[];
}

export function fetchCompliance(): Promise<ComplianceResponse> {
  return request<ComplianceResponse>("/api/partners/compliance");
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
