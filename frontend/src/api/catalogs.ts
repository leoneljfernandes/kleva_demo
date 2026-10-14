import { useQuery } from "@tanstack/react-query";
import { useCallback } from "react";
import { api } from "./client";
import type { Catalogs } from "./types";

export function useCatalogs() {
  return useQuery({
    queryKey: ["catalogs"],
    queryFn: () => api<Catalogs>("/catalogs"),
    staleTime: Infinity, // los enums no cambian mientras la app está abierta
  });
}

type Group = Exclude<keyof Catalogs, never>;

/** Labels siempre desde /catalogs, nunca de un mapa armado en el cliente. */
export function useLabels() {
  const { data } = useCatalogs();
  const label = useCallback(
    (group: Group, value: string | null | undefined) => {
      if (!value) return "";
      return data?.[group].find((option) => option.value === value)?.label ?? value;
    },
    [data],
  );
  const currency = useCallback(
    (country: string) => data?.countries.find((c) => c.value === country)?.currency ?? "USD",
    [data],
  );
  return { label, currency, ready: Boolean(data) };
}
