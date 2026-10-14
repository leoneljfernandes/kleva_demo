import type { ReactNode } from "react";
import styles from "./Orb.module.css";

/** Esfera en CSS (reemplaza la imagen de kleva.co). Late cuando el agente está activo. */
export function Orb({ live = false }: { live?: boolean }) {
  return <div className={`${styles.orb} ${live ? styles.live : ""}`} aria-hidden="true" />;
}

/** Panel lila con la esfera a la izquierda y, si hay, la tarjeta del agente a la derecha. */
export function AgentStage({ live = false, children }: { live?: boolean; children?: ReactNode }) {
  return (
    <section className={`${styles.stage} ${children ? "" : styles.solo}`}>
      <Orb live={live} />
      {children}
    </section>
  );
}
