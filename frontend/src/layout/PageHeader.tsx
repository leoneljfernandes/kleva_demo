import type { ReactNode } from "react";
import styles from "./PageHeader.module.css";

/** Encabezado de kleva.co: eyebrow, h1 a la izquierda y bajada a la derecha. */
export function PageHeader({
  eyebrow,
  title,
  intro,
  actions,
}: {
  eyebrow: string;
  title: ReactNode;
  intro?: ReactNode;
  actions?: ReactNode;
}) {
  return (
    <header className={styles.header}>
      <span className={`eyebrow ${styles.eyebrow}`}>{eyebrow}</span>
      <h1 className="enter">{title}</h1>
      {intro && <p className={`enter ${styles.intro}`}>{intro}</p>}
      {actions && <div className={styles.actions}>{actions}</div>}
    </header>
  );
}
