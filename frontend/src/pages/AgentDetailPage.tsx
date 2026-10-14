import { Fragment, useState } from "react";
import { useParams } from "react-router";
import { useAgent, useAgentCalls, useAgentStats, useCallNow, useSetAgentStatus } from "../api/agents";
import { useLabels } from "../api/catalogs";
import type { Agent, Call } from "../api/types";
import { AgentCard } from "../components/AgentCard";
import { AgentStage } from "../components/AgentStage";
import { Button, ButtonLink } from "../components/Button";
import { OutcomeBadge } from "../components/OutcomeBadge";
import { StatCard, StatGrid } from "../components/StatCard";
import tableStyles from "../components/Table.module.css";
import { TranscriptView } from "../components/TranscriptView";
import { PageHeader } from "../layout/PageHeader";
import { parseFormError } from "../lib/errors";
import { formatDate, formatDateTime, formatDuration, formatMoney } from "../lib/format";
import { NotFound } from "./AgentFormPage";
import styles from "./pages.module.css";

export function AgentDetailPage() {
  const id = Number(useParams().id);
  const agent = useAgent(id);
  const live = agent.data?.status === "active";
  const calls = useAgentCalls(id, live);
  const stats = useAgentStats(id, live);
  const { label, currency } = useLabels();

  if (agent.isError) return <NotFound />;
  if (!agent.data) return <p className={styles.state}>Cargando…</p>;
  const money = (amount: string | null | undefined) => formatMoney(amount, currency(agent.data.country));

  return (
    <>
      <PageHeader
        eyebrow="Agente de cobranza"
        title={agent.data.name}
        intro={
          <>
            Llama a deudores de {label("product_types", agent.data.product_type).toLowerCase()} en{" "}
            {label("countries", agent.data.country)} con {agent.data.min_days_overdue} días de atraso o más, con un
            estilo {label("negotiation_styles", agent.data.negotiation_style).toLowerCase()}.
          </>
        }
      />

      <AgentStage live={live}>
        <AgentControls agent={agent.data} />
      </AgentStage>

      <section className={styles.section}>
        <StatGrid>
          <StatCard label="Llamadas" value={stats.data?.total ?? "—"} />
          <StatCard
            label="Promesas de pago"
            value={stats.data?.payment_promise ?? "—"}
            hint={stats.data && `${money(stats.data.promised_amount_total)} prometidos`}
          />
          <StatCard label="No atendió" value={stats.data?.no_answer ?? "—"} />
          <StatCard label="No abonará" value={stats.data?.refused ?? "—"} />
        </StatGrid>
      </section>

      <section className={styles.section}>
        <div className={styles.sectionHead}>
          <h2>Llamadas</h2>
          {live && <span className="muted">Actualizando en vivo</span>}
        </div>
        <div className={`card ${tableStyles.wrap}`}>
          {calls.isLoading ? (
            <p className={tableStyles.empty}>Cargando llamadas…</p>
          ) : !calls.data?.length ? (
            <p className={tableStyles.empty}>
              Todavía no hay llamadas. Activá el agente o usá “Llamar ahora”.
            </p>
          ) : (
            <CallsTable calls={calls.data} agentName={agent.data.name} money={money} />
          )}
        </div>
      </section>
    </>
  );
}

function AgentControls({ agent }: { agent: Agent }) {
  const setStatus = useSetAgentStatus();
  const callNow = useCallNow(agent.id);
  const { label } = useLabels();
  const [notice, setNotice] = useState<string>();
  const isActive = agent.status === "active";

  function placeCall() {
    setNotice(undefined);
    callNow.mutate(undefined, {
      onSuccess: (call) =>
        setNotice(
          call
            ? `${label("call_outcomes", call.outcome)} · ${call.debtor.first_name} ${call.debtor.last_name}`
            : "No hay deudores elegibles en este momento.",
        ),
      onError: (error) => setNotice(parseFormError(error).general),
    });
  }

  return (
    <AgentCard
      agent={agent}
      notice={notice}
      actions={
        <>
          <Button
            variant="secondary"
            disabled={setStatus.isPending}
            onClick={() => setStatus.mutate({ id: agent.id, active: !isActive })}
          >
            {isActive ? "Pausar" : "Activar"}
          </Button>
          <Button arrow disabled={callNow.isPending} onClick={placeCall}>
            {callNow.isPending ? "Llamando…" : "Llamar ahora"}
          </Button>
          {!isActive && (
            <ButtonLink variant="link" to={`/agents/${agent.id}/edit`}>
              Editar
            </ButtonLink>
          )}
        </>
      }
    />
  );
}

function CallsTable({
  calls,
  agentName,
  money,
}: {
  calls: Call[];
  agentName: string;
  money: (amount: string | null | undefined) => string;
}) {
  const [open, setOpen] = useState<number | null>(null);
  return (
    <table className={tableStyles.table}>
      <thead>
        <tr>
          <th>Fecha</th>
          <th>Deudor</th>
          <th>Resultado</th>
          <th>Promesa</th>
          <th className={tableStyles.num}>Duración</th>
          <th>
            <span className="visually-hidden">Transcript</span>
          </th>
        </tr>
      </thead>
      <tbody>
        {calls.map((call) => (
          <Fragment key={call.id}>
            <tr>
              <td data-label="Fecha" className="mono">
                {formatDateTime(call.started_at)}
              </td>
              <td data-label="Deudor">
                <span className={styles.debtor}>
                  {call.debtor.first_name} {call.debtor.last_name}
                  <span className={`mono ${styles.subtle}`}>DNI {call.debtor.dni}</span>
                </span>
              </td>
              <td data-label="Resultado">
                <OutcomeBadge outcome={call.outcome} />
              </td>
              <td data-label="Promesa" className="mono">
                {call.outcome === "payment_promise" && call.promised_date
                  ? `${money(call.promised_amount)} · ${formatDate(call.promised_date)} (${call.promised_days} d)`
                  : "—"}
              </td>
              <td data-label="Duración" className={`mono ${tableStyles.num}`}>
                {formatDuration(call.duration_seconds)}
              </td>
              <td data-label="">
                <Button
                  variant="link"
                  size="sm"
                  aria-expanded={open === call.id}
                  onClick={() => setOpen(open === call.id ? null : call.id)}
                >
                  {open === call.id ? "Ocultar" : "Ver transcript"}
                </Button>
              </td>
            </tr>
            {open === call.id && (
              <tr>
                <td colSpan={6} data-label="" className={styles.transcriptCell}>
                  <TranscriptView lines={call.transcript} agentName={agentName} />
                </td>
              </tr>
            )}
          </Fragment>
        ))}
      </tbody>
    </table>
  );
}
