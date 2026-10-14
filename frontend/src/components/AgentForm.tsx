import { useState, type FormEvent } from "react";
import type { Agent, AgentCreate, Catalogs } from "../api/types";
import type { FormErrors } from "../lib/errors";
import styles from "../pages/pages.module.css";
import { Button } from "./Button";
import { SelectField, TextField } from "./Field";

type Values = Record<keyof AgentCreate, string>;

const EMPTY: Values = {
  name: "",
  agent_type: "",
  product_type: "",
  country: "",
  negotiation_style: "",
  min_days_overdue: "30",
};

function fromAgent(agent: Agent): Values {
  return {
    name: agent.name,
    agent_type: agent.agent_type,
    product_type: agent.product_type,
    country: agent.country,
    negotiation_style: agent.negotiation_style,
    min_days_overdue: String(agent.min_days_overdue),
  };
}

export function AgentForm({
  catalogs,
  initial,
  disabled = false,
  submitting = false,
  errors,
  onSubmit,
  onCancel,
}: {
  catalogs: Catalogs;
  initial?: Agent;
  disabled?: boolean;
  submitting?: boolean;
  errors: FormErrors;
  onSubmit: (data: AgentCreate) => void;
  onCancel: () => void;
}) {
  const [values, setValues] = useState<Values>(() => (initial ? fromAgent(initial) : EMPTY));
  const [touched, setTouched] = useState(false);

  // El producto depende del tipo: solo se ofrecen los de su categoría
  const products = catalogs.product_types.filter((p) => p.agent_type === values.agent_type);

  function set(field: keyof Values, value: string) {
    setValues((current) => {
      const next = { ...current, [field]: value };
      if (field === "agent_type") {
        const stillValid = catalogs.product_types.some(
          (p) => p.value === current.product_type && p.agent_type === value,
        );
        if (!stillValid) next.product_type = "";
      }
      return next;
    });
  }

  const missing = (field: keyof Values) => (touched && values[field].trim() === "" ? "Campo obligatorio." : undefined);
  const error = (field: keyof Values) => errors.fields[field] ?? missing(field);

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setTouched(true);
    if (Object.values(values).some((value) => value.trim() === "")) return;
    onSubmit({
      name: values.name.trim(),
      agent_type: values.agent_type as AgentCreate["agent_type"],
      product_type: values.product_type as AgentCreate["product_type"],
      country: values.country as AgentCreate["country"],
      negotiation_style: values.negotiation_style as AgentCreate["negotiation_style"],
      min_days_overdue: Number(values.min_days_overdue),
    });
  }

  return (
    <form className={`card ${styles.formCard}`} onSubmit={handleSubmit} noValidate>
      <fieldset disabled={disabled} className={styles.fieldset}>
        <div className={styles.formGrid}>
          <div className={styles.span2}>
            <TextField
              label="Nombre"
              value={values.name}
              maxLength={80}
              placeholder="Ej.: Valeria"
              onChange={(e) => set("name", e.target.value)}
              error={error("name")}
            />
          </div>
          <SelectField
            label="Tipo de agente"
            value={values.agent_type}
            placeholder="Elegí un tipo"
            options={catalogs.agent_types}
            onChange={(e) => set("agent_type", e.target.value)}
            error={error("agent_type")}
          />
          <SelectField
            label="Producto"
            value={values.product_type}
            placeholder={values.agent_type ? "Elegí un producto" : "Elegí primero el tipo"}
            options={products}
            disabled={!values.agent_type}
            onChange={(e) => set("product_type", e.target.value)}
            error={error("product_type")}
          />
          <SelectField
            label="País"
            value={values.country}
            placeholder="Elegí un país"
            options={catalogs.countries}
            onChange={(e) => set("country", e.target.value)}
            error={error("country")}
          />
          <SelectField
            label="Estilo de negociación"
            value={values.negotiation_style}
            placeholder="Elegí un estilo"
            options={catalogs.negotiation_styles}
            onChange={(e) => set("negotiation_style", e.target.value)}
            error={error("negotiation_style")}
          />
          <TextField
            label="Días mínimos de atraso"
            type="number"
            min={0}
            max={3650}
            inputMode="numeric"
            value={values.min_days_overdue}
            onChange={(e) => set("min_days_overdue", e.target.value)}
            error={error("min_days_overdue")}
            hint="Llama solo a deudores con al menos estos días de atraso."
          />
        </div>
      </fieldset>
      {errors.general && (
        <p className={`${styles.alert} ${styles.formAlert}`} role="alert">
          {errors.general}
        </p>
      )}
      <div className={styles.formActions}>
        <Button variant="secondary" onClick={onCancel}>
          Cancelar
        </Button>
        <Button type="submit" arrow disabled={disabled || submitting}>
          {submitting ? "Guardando…" : "Guardar"}
        </Button>
      </div>
    </form>
  );
}
