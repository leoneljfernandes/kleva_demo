import { useLabels } from "../api/catalogs";
import styles from "./Badge.module.css";

export function StatusBadge({ status }: { status: string }) {
  const { label } = useLabels();
  return (
    <span className={`${styles.status} ${styles[status] ?? ""}`}>
      <span className={styles.dot} aria-hidden="true" />
      {label("agent_statuses", status)}
    </span>
  );
}
