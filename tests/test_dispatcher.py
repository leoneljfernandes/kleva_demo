"""El dispatcher se prueba llamando tick() directo: sin sleep y sin tarea en background."""

from app.domain.enums import Country, ProductType
from app.services.dispatcher import CallDispatcher
from tests.conftest import make_debtor


def make_dispatcher(session_factory, call_engine, clock) -> CallDispatcher:
    return CallDispatcher(session_factory, call_engine, interval=0.01, clock=clock)


def start(client, headers, agent):
    assert client.post(f"/api/agents/{agent['id']}/start", headers=headers).status_code == 200


def test_tick_places_one_call_per_active_agent(
    client, auth_headers, create_agent, db_add, session_factory, call_engine, clock
):
    valeria = create_agent()
    mateo = create_agent(name="Mateo", country="MX", agent_type="services", product_type="internet")
    db_add(
        make_debtor(),
        make_debtor(),
        make_debtor(country=Country.MX, product_type=ProductType.INTERNET),
    )
    start(client, auth_headers, valeria)
    start(client, auth_headers, mateo)

    placed = client.portal.call(make_dispatcher(session_factory, call_engine, clock).tick)

    assert placed == 2
    assert {agent.name for agent, _ in call_engine.received} == {"Valeria", "Mateo"}


def test_paused_agents_are_not_dispatched(client, create_agent, db_add, session_factory, call_engine, clock):
    create_agent()
    db_add(make_debtor())
    assert client.portal.call(make_dispatcher(session_factory, call_engine, clock).tick) == 0
    assert call_engine.received == []


def test_two_agents_never_call_the_same_debtor_in_one_tick(
    client, auth_headers, create_agent, db_add, session_factory, call_engine, clock
):
    start(client, auth_headers, create_agent())
    start(client, auth_headers, create_agent(name="Valeria 2"))
    db_add(make_debtor())

    assert client.portal.call(make_dispatcher(session_factory, call_engine, clock).tick) == 1


def test_agent_stays_active_without_eligible_debtors(
    client, auth_headers, create_agent, session_factory, call_engine, clock
):
    agent = create_agent()
    start(client, auth_headers, agent)

    assert client.portal.call(make_dispatcher(session_factory, call_engine, clock).tick) == 0
    assert client.get(f"/api/agents/{agent['id']}", headers=auth_headers).json()["status"] == "active"
