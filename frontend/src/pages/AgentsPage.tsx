import { Link } from "react-router";
import { useAgents, useDeleteAgent, useSetAgentStatus } from "../api/agents";
import { useLabels } from "../api/catalogs";
import { Button, ButtonLink } from "../components/Button";
import { ConfirmButton } from "../components/ConfirmButton";
import { StatCard, StatGrid } from "../components/StatCard";
import { StatusBadge } from "../components/StatusBadge";
import tableStyles from "../components/Table.module.css";
import { PageHeader } from "../layout/PageHeader";
import styles from "./pages.module.css";

const PAUSE_FIRST = "Pausá el agente para editarlo o eliminarlo";

export function AgentsPage() {
  const agents = useAgents();
  const setStatus = useSetAgentStatus();
  const deleteAgent = useDeleteAgent();
  const { label } = useLabels();

  const list = agents.data ?? [];
  const active = list.filter((a) => a.status === "active").length;
  const countries = new Set(list.map((a) => a.country)).size;

  return (
    <>
      <PageHeader
        eyebrow="Agentes de cobranza"
        title="Tus agentes."
        intro="Configurá a quién llama cada agente y activalo para que salga a buscar deudores."
        actions={
          <ButtonLink to="/agents/new" arrow>
            Nuevo agente
          </ButtonLink>
        }
      />

      <StatGrid>
        <StatCard label="Agentes" value={list.length} />
        <StatCard label="Activos" value={active} />
        <StatCard label="Pausados" value={list.length - active} />
        <StatCard label="Países" value={countries} />
      </StatGrid>

      <section className={styles.section}>
        <div className={`card ${tableStyles.wrap}`}>
          {agents.isLoading ? (
            <p className={tableStyles.empty}>Cargando agentes…</p>
          ) : agents.isError ? (
            <p className={tableStyles.empty}>No se pudieron cargar los agentes.</p>
          ) : list.length === 0 ? (
            <p className={tableStyles.empty}>Todavía no hay agentes. Creá el primero.</p>
          ) : (
            <table className={tableStyles.table}>
              <thead>
                <tr>
                  <th>Nombre</th>
                  <th>Tipo</th>
                  <th>País</th>
                  <th>Producto</th>
                  <th>Estilo</th>
                  <th className={tableStyles.num}>Días mín.</th>
                  <th>Estado</th>
                  <th>
                    <span className="visually-hidden">Acciones</span>
                  </th>
                </tr>
              </thead>
              <tbody>
                {list.map((agent) => {
                  const isActive = agent.status === "active";
                  return (
                    <tr key={agent.id}>
                      <td data-label="Nombre">
                        <Link to={`/agents/${agent.id}`} className={tableStyles.nameLink}>
                          {agent.name}
                        </Link>
                      </td>
                      <td data-label="Tipo">{label("agent_types", agent.agent_type)}</td>
                      <td data-label="País">{label("countries", agent.country)}</td>
                      <td data-label="Producto">{label("product_types", agent.product_type)}</td>
                      <td data-label="Estilo">{label("negotiation_styles", agent.negotiation_style)}</td>
                      <td data-label="Días mín." className={`mono ${tableStyles.num}`}>
                        {agent.min_days_overdue}
                      </td>
                      <td data-label="Estado">
                        <StatusBadge status={agent.status} />
                      </td>
                      <td data-label="">
                        <div className={tableStyles.actions}>
                          <Button
                            size="sm"
                            variant={isActive ? "secondary" : "primary"}
                            disabled={setStatus.isPending}
                            onClick={() => setStatus.mutate({ id: agent.id, active: !isActive })}
                          >
                            {isActive ? "Pausar" : "Activar"}
                          </Button>
                          {isActive ? (
                            <Button size="sm" variant="secondary" disabled title={PAUSE_FIRST}>
                              Editar
                            </Button>
                          ) : (
                            <ButtonLink size="sm" variant="secondary" to={`/agents/${agent.id}/edit`}>
                              Editar
                            </ButtonLink>
                          )}
                          <ConfirmButton
                            size="sm"
                            variant="secondary"
                            disabled={isActive || deleteAgent.isPending}
                            title={isActive ? PAUSE_FIRST : undefined}
                            confirmLabel="¿Eliminar?"
                            onConfirm={() => deleteAgent.mutate(agent.id)}
                          >
                            Eliminar
                          </ConfirmButton>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>
      </section>
    </>
  );
}
