import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, json } from "./client";
import type { Agent, AgentCreate, AgentStats, AgentUpdate, Call } from "./types";

const LIVE_REFRESH_MS = 3000;

export const agentKeys = {
  all: ["agents"] as const,
  detail: (id: number) => ["agents", id] as const,
  calls: (id: number) => ["agents", id, "calls"] as const,
  stats: (id: number) => ["agents", id, "stats"] as const,
};

export function useAgents() {
  return useQuery({ queryKey: agentKeys.all, queryFn: () => api<Agent[]>("/agents") });
}

export function useAgent(id: number) {
  return useQuery({ queryKey: agentKeys.detail(id), queryFn: () => api<Agent>(`/agents/${id}`) });
}

/** Con el agente activo, polling cada 3 s: las llamadas aparecen sin recargar. Pausado, nada. */
export function useAgentCalls(id: number, live: boolean) {
  return useQuery({
    queryKey: agentKeys.calls(id),
    queryFn: () => api<Call[]>(`/agents/${id}/calls?limit=100`),
    refetchInterval: live ? LIVE_REFRESH_MS : false,
  });
}

export function useAgentStats(id: number, live: boolean) {
  return useQuery({
    queryKey: agentKeys.stats(id),
    queryFn: () => api<AgentStats>(`/agents/${id}/stats`),
    refetchInterval: live ? LIVE_REFRESH_MS : false,
  });
}

// Toda mutación invalida el prefijo ["agents"]: lista, detalle, llamadas y stats se recargan solos.
function useInvalidateAgents() {
  const queryClient = useQueryClient();
  return () => queryClient.invalidateQueries({ queryKey: agentKeys.all });
}

export function useCreateAgent() {
  const invalidate = useInvalidateAgents();
  return useMutation({
    mutationFn: (data: AgentCreate) => api<Agent>("/agents", { method: "POST", body: json(data) }),
    onSuccess: invalidate,
  });
}

export function useUpdateAgent(id: number) {
  const invalidate = useInvalidateAgents();
  return useMutation({
    mutationFn: (data: AgentUpdate) => api<Agent>(`/agents/${id}`, { method: "PATCH", body: json(data) }),
    onSuccess: invalidate,
  });
}

export function useDeleteAgent() {
  const invalidate = useInvalidateAgents();
  return useMutation({
    mutationFn: (id: number) => api<void>(`/agents/${id}`, { method: "DELETE" }),
    onSuccess: invalidate,
  });
}

export function useSetAgentStatus() {
  const invalidate = useInvalidateAgents();
  return useMutation({
    mutationFn: ({ id, active }: { id: number; active: boolean }) =>
      api<Agent>(`/agents/${id}/${active ? "start" : "pause"}`, { method: "POST" }),
    onSuccess: invalidate,
  });
}

/** Llamada manual: devuelve undefined (204) si no hay deudores elegibles. */
export function useCallNow(id: number) {
  const invalidate = useInvalidateAgents();
  return useMutation({
    mutationFn: () => api<Call | undefined>(`/agents/${id}/calls`, { method: "POST" }),
    onSuccess: invalidate,
  });
}
