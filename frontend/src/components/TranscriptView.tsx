import type { TranscriptLine } from "../api/types";
import styles from "./TranscriptView.module.css";

const SPEAKER = { agent: "Agente", debtor: "Deudor" } as const;

export function TranscriptView({ lines, agentName }: { lines: TranscriptLine[]; agentName: string }) {
  return (
    <ol className={styles.transcript} aria-label="Transcript de la llamada">
      {lines.map((line, index) => (
        <li key={index} className={`${styles.line} ${styles[line.speaker]}`}>
          {line.speaker !== "system" && (
            <span className={styles.speaker}>{line.speaker === "agent" ? agentName : SPEAKER.debtor}</span>
          )}
          {line.text}
        </li>
      ))}
    </ol>
  );
}
