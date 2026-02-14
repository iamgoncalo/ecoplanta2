import { useQuery } from "@tanstack/react-query";
import { fetchHealth } from "@/api/client.ts";
import type { HealthResponse } from "@/api/client.ts";

export function useHealth() {
  return useQuery<HealthResponse>({
    queryKey: ["health"],
    queryFn: fetchHealth,
    refetchInterval: 10_000,
    retry: 1,
  });
}
