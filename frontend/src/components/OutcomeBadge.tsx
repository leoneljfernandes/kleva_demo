import { useLabels } from "../api/catalogs";
import styles from "./Badge.module.css";

export function OutcomeBadge({ outcome }: { outcome: string }) {
  const { label } = useLabels();
  return <span className={`${styles.outcome} ${styles[outcome] ?? ""}`}>{label("call_outcomes", outcome)}</span>;
}
