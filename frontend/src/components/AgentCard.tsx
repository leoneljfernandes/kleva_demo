import type { ReactNode } from "react";
import { useLabels } from "../api/catalogs";
import type { Agent } from "../api/types";
import styles from "./AgentCard.module.css";
import { StatusBadge } from "./StatusBadge";

/** Versión de dominio de la tarjeta "Valeria · Agente de cobranza · Argentina · Español · ARS". */
export function AgentCard({ agent, actions, notice }: { agent: Agent; actions?: ReactNode; notice?: ReactNode }) {
  const { label } = useLabels();
  return (
    <article className={styles.card} aria-label={`Agente ${agent.name}`}>
      <h2>{agent.name}</h2>
      <p className={styles.role}>
        Agente de cobranza · {label("countries", agent.country)}
      </p>
      <p className={`mono ${styles.meta}`}>
        {label("agent_types", agent.agent_type)} · {label("product_types", agent.product_type)} ·{" "}
        {label("negotiation_styles", agent.negotiation_style)} · +{agent.min_days_overdue} días
      </p>
      <div className={styles.status}>
        <StatusBadge status={agent.status} />
      </div>
      {actions && <div className={styles.actions}>{actions}</div>}
      {notice && (
        <p className={styles.notice} role="status">
          {notice}
        </p>
      )}
    </article>
  );
}
