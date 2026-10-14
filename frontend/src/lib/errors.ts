import { ApiError } from "../api/client";
import type { ValidationErrorItem } from "../api/types";

const MESSAGES: Record<string, string> = {
  missing: "Campo obligatorio.",
  string_too_short: "No puede quedar vacío.",
  string_too_long: "Es demasiado largo.",
  greater_than_equal: "Tiene que ser 0 o más.",
  less_than_equal: "Es demasiado grande.",
  int_parsing: "Tiene que ser un número entero.",
  enum: "Elegí una opción válida.",
};

export interface FormErrors {
  fields: Record<string, string>;
  general?: string;
}

/** 422 de FastAPI → error por campo; validaciones de modelo y errores de dominio → mensaje general. */
export function parseFormError(error: unknown): FormErrors {
  if (!(error instanceof ApiError)) return { fields: {}, general: "No se pudo conectar con el servidor." };
  if (Array.isArray(error.detail)) {
    const fields: Record<string, string> = {};
    let general: string | undefined;
    for (const item of error.detail as ValidationErrorItem[]) {
      const field = item.loc.length > 1 ? String(item.loc[item.loc.length - 1]) : undefined;
      const message = MESSAGES[item.type] ?? item.msg.replace(/^Value error, /, "");
      if (field && field !== "body") fields[field] ??= message;
      else general = message;
    }
    return { fields, general };
  }
  return { fields: {}, general: error.message };
}
