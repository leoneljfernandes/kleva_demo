const LOCALE = "es-AR";

/** Montos llegan como string (Decimal): se formatean, nunca se usan para hacer cuentas. */
export function formatMoney(amount: string | null | undefined, currency: string): string {
  if (amount == null) return "—";
  return new Intl.NumberFormat(LOCALE, { style: "currency", currency, maximumFractionDigits: 2 }).format(
    Number(amount),
  );
}

/** Fechas llegan en UTC (ISO) y se muestran en la hora local del navegador. */
export function formatDateTime(iso: string): string {
  return new Intl.DateTimeFormat(LOCALE, { dateStyle: "short", timeStyle: "medium" }).format(new Date(iso));
}

export function formatDate(isoDate: string): string {
  // "2026-10-24" es una fecha sin hora: se interpreta como local para no correrla un día
  const [year, month, day] = isoDate.split("-").map(Number);
  return new Intl.DateTimeFormat(LOCALE, { dateStyle: "medium" }).format(new Date(year, month - 1, day));
}

export function formatDuration(seconds: number): string {
  const minutes = Math.floor(seconds / 60);
  return `${minutes}:${String(seconds % 60).padStart(2, "0")}`;
}
