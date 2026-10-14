import { useState } from "react";
import { useNavigate, useParams } from "react-router";
import { useAgent, useCreateAgent, useUpdateAgent } from "../api/agents";
import { useCatalogs } from "../api/catalogs";
import type { AgentCreate } from "../api/types";
import { AgentForm } from "../components/AgentForm";
import { ButtonLink } from "../components/Button";
import { parseFormError, type FormErrors } from "../lib/errors";
import { PageHeader } from "../layout/PageHeader";
import styles from "./pages.module.css";

const NO_ERRORS: FormErrors = { fields: {} };

export function NewAgentPage() {
  const navigate = useNavigate();
  const catalogs = useCatalogs();
  const create = useCreateAgent();
  const [errors, setErrors] = useState(NO_ERRORS);

  function submit(data: AgentCreate) {
    setErrors(NO_ERRORS);
    create.mutate(data, {
      onSuccess: (agent) => navigate(`/agents/${agent.id}`),
      onError: (error) => setErrors(parseFormError(error)),
    });
  }

  return (
    <>
      <PageHeader
        eyebrow="Nuevo agente"
        title="Configurá un agente."
        intro="Elegí el producto, el país y desde cuántos días de atraso llama. El agente se crea pausado."
      />
      {catalogs.data ? (
        <AgentForm
          catalogs={catalogs.data}
          errors={errors}
          submitting={create.isPending}
          onSubmit={submit}
          onCancel={() => navigate("/agents")}
        />
      ) : (
        <p className={styles.state}>Cargando…</p>
      )}
    </>
  );
}

export function EditAgentPage() {
  const id = Number(useParams().id);
  const navigate = useNavigate();
  const catalogs = useCatalogs();
  const agent = useAgent(id);
  const update = useUpdateAgent(id);
  const [errors, setErrors] = useState(NO_ERRORS);

  function submit(data: AgentCreate) {
    setErrors(NO_ERRORS);
    update.mutate(data, {
      onSuccess: () => navigate(`/agents/${id}`),
      onError: (error) => setErrors(parseFormError(error)),
    });
  }

  if (agent.isError) return <NotFound />;
  if (!agent.data || !catalogs.data) return <p className={styles.state}>Cargando…</p>;
  const isActive = agent.data.status === "active";

  return (
    <>
      <PageHeader
        eyebrow="Editar agente"
        title={agent.data.name}
        intro={isActive ? undefined : "Los cambios aplican desde la próxima llamada."}
      />
      {isActive && (
        <p className={`${styles.info} ${styles.noticeBlock}`} role="status">
          El agente está activo. Pausalo para poder editarlo.
        </p>
      )}
      <AgentForm
        key={agent.data.id}
        catalogs={catalogs.data}
        initial={agent.data}
        disabled={isActive}
        errors={errors}
        submitting={update.isPending}
        onSubmit={submit}
        onCancel={() => navigate(`/agents/${id}`)}
      />
    </>
  );
}

export function NotFound() {
  return (
    <PageHeader
      eyebrow="404"
      title="No encontramos ese agente."
      intro="Puede que haya sido eliminado."
      actions={
        <ButtonLink to="/agents" variant="secondary">
          Volver a agentes
        </ButtonLink>
      }
    />
  );
}
