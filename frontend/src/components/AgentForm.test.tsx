import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import type { Agent, Catalogs } from "../api/types";
import { AgentForm } from "./AgentForm";

const catalogs: Catalogs = {
  countries: [
    { value: "AR", label: "Argentina", currency: "ARS" },
    { value: "US", label: "Estados Unidos", currency: "USD" },
  ],
  agent_types: [
    { value: "financial", label: "Financiero" },
    { value: "services", label: "Servicios" },
  ],
  product_types: [
    { value: "credit_card", label: "Tarjeta de crédito", agent_type: "financial" },
    { value: "personal_loan", label: "Préstamo personal", agent_type: "financial" },
    { value: "internet", label: "Internet", agent_type: "services" },
  ],
  negotiation_styles: [
    { value: "soft", label: "Suave" },
    { value: "strict", label: "Rígido" },
  ],
  agent_statuses: [],
  call_outcomes: [],
};

function renderForm(props: Partial<Parameters<typeof AgentForm>[0]> = {}) {
  const onSubmit = vi.fn();
  render(<AgentForm catalogs={catalogs} onSubmit={onSubmit} onCancel={() => {}} errors={{ fields: {} }} {...props} />);
  return { onSubmit, user: userEvent.setup() };
}

const productOptions = () =>
  Array.from((screen.getByLabelText("Producto") as HTMLSelectElement).options)
    .filter((option) => !option.disabled)
    .map((option) => option.value);

describe("AgentForm", () => {
  it("filtra los productos por el tipo de agente elegido", async () => {
    const { user } = renderForm();
    expect(screen.getByLabelText("Producto")).toBeDisabled();

    await user.selectOptions(screen.getByLabelText("Tipo de agente"), "financial");
    expect(productOptions()).toEqual(["credit_card", "personal_loan"]);

    await user.selectOptions(screen.getByLabelText("Tipo de agente"), "services");
    expect(productOptions()).toEqual(["internet"]);
  });

  it("limpia el producto si deja de corresponder al tipo", async () => {
    const { user } = renderForm();
    await user.selectOptions(screen.getByLabelText("Tipo de agente"), "financial");
    await user.selectOptions(screen.getByLabelText("Producto"), "credit_card");

    await user.selectOptions(screen.getByLabelText("Tipo de agente"), "services");

    expect(screen.getByLabelText("Producto")).toHaveValue("");
  });

  it("envía el agente con los días como número", async () => {
    const { user, onSubmit } = renderForm();
    await user.type(screen.getByLabelText("Nombre"), "Valeria");
    await user.selectOptions(screen.getByLabelText("Tipo de agente"), "financial");
    await user.selectOptions(screen.getByLabelText("Producto"), "credit_card");
    await user.selectOptions(screen.getByLabelText("País"), "AR");
    await user.selectOptions(screen.getByLabelText("Estilo de negociación"), "soft");
    await user.clear(screen.getByLabelText("Días mínimos de atraso"));
    await user.type(screen.getByLabelText("Días mínimos de atraso"), "45");

    await user.click(screen.getByRole("button", { name: /guardar/i }));

    expect(onSubmit).toHaveBeenCalledWith({
      name: "Valeria",
      agent_type: "financial",
      product_type: "credit_card",
      country: "AR",
      negotiation_style: "soft",
      min_days_overdue: 45,
    });
  });

  it("no envía con campos vacíos", async () => {
    const { user, onSubmit } = renderForm();
    await user.click(screen.getByRole("button", { name: /guardar/i }));
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("precarga un agente existente y muestra errores del servidor por campo", () => {
    const agent = {
      id: 1, name: "Mateo", agent_type: "services", product_type: "internet", country: "US",
      negotiation_style: "strict", min_days_overdue: 15, status: "paused", created_at: "", updated_at: null,
    } as Agent;
    renderForm({ initial: agent, errors: { fields: { name: "No puede quedar vacío." } } });

    expect(screen.getByLabelText("Nombre")).toHaveValue("Mateo");
    expect(screen.getByLabelText("Producto")).toHaveValue("internet");
    expect(screen.getByText("No puede quedar vacío.")).toBeInTheDocument();
  });
});
