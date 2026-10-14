import type { ReactNode } from "react";
import styles from "./StatCard.module.css";

export function StatGrid({ children }: { children: ReactNode }) {
  return <div className={styles.grid}>{children}</div>;
}

export function StatCard({ label, value, hint }: { label: string; value: ReactNode; hint?: ReactNode }) {
  return (
    <div className={`card ${styles.card}`}>
      <span className={`eyebrow ${styles.label}`}>{label}</span>
      <span className={styles.value}>{value}</span>
      {hint && <span className={`mono ${styles.hint}`}>{hint}</span>}
    </div>
  );
}
