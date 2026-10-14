import random
from datetime import datetime, timedelta

from app.api.deps import get_call_engine
from app.domain.enums import CallOutcome, Country, ProductType
from app.main import app
from app.services.call_engine.simulated import SimulatedCallEngine
from tests.conftest import make_debtor


def call_now(client, headers, agent_id):
    return client.post(f"/api/agents/{agent_id}/calls", headers=headers)


def get_debtor(client, headers, debtor_id) -> dict:
    return client.get(f"/api/debtors/{debtor_id}", headers=headers).json()


def test_promise_sets_next_contact_after_promised_date(
    client, auth_headers, create_agent, db_add, call_engine, clock
):
    agent = create_agent()
    [debtor] = db_add(make_debtor())
    call_engine.set(CallOutcome.PAYMENT_PROMISE, promised_days=10, promised_amount="900.00")

    response = call_now(client, auth_headers, agent["id"])

    assert response.status_code == 201
    body = response.json()
    assert body["outcome"] == "payment_promise"
    assert body["promised_days"] == 10
    assert body["promised_date"] == (clock.now + timedelta(days=10)).date().isoformat()
    assert body["promised_amount"] == "900.00"
    assert body["debtor"]["id"] == debtor.id
    assert body["agent"]["name"] == "Valeria"
    updated = get_debtor(client, auth_headers, debtor.id)
    assert datetime.fromisoformat(updated["next_contact_at"]) == clock.now + timedelta(days=11)
    assert updated["last_call_outcome"] == "payment_promise"
    assert updated["balance"] == "1000.00"  # la emulación nunca toca el saldo


def test_no_answer_retries_after_configured_minutes(
    client, auth_headers, create_agent, db_add, call_engine, clock
):
    agent = create_agent()
    db_add(make_debtor())
    call_engine.set(CallOutcome.NO_ANSWER)

    assert call_now(client, auth_headers, agent["id"]).status_code == 201
    assert call_now(client, auth_headers, agent["id"]).status_code == 204  # en reintento
    clock.advance(minutes=30)
    assert call_now(client, auth_headers, agent["id"]).status_code == 201


def test_refused_enters_cooldown(client, auth_headers, create_agent, db_add, call_engine, clock):
    agent = create_agent()
    db_add(make_debtor())
    call_engine.set(CallOutcome.REFUSED)

    assert call_now(client, auth_headers, agent["id"]).status_code == 201
    clock.advance(days=6, hours=23)
    assert call_now(client, auth_headers, agent["id"]).status_code == 204
    clock.advance(hours=1)
    assert call_now(client, auth_headers, agent["id"]).status_code == 201


def test_only_debtors_matching_agent_config_are_called(
    client, auth_headers, create_agent, db_add, call_engine
):
    agent = create_agent(min_days_overdue=30)  # AR + credit_card
    db_add(
        make_debtor(country=Country.CL),
        make_debtor(product_type=ProductType.PERSONAL_LOAN),
        make_debtor(days_overdue=29),
    )
    assert call_now(client, auth_headers, agent["id"]).status_code == 204

    [match] = db_add(make_debtor(days_overdue=30))
    response = call_now(client, auth_headers, agent["id"])
    assert response.status_code == 201
    assert response.json()["debtor"]["id"] == match.id


def test_oldest_then_largest_debt_is_called_first(client, auth_headers, create_agent, db_add):
    agent = create_agent()
    small, big, oldest = db_add(
        make_debtor(days_overdue=60, balance="100.00"),
        make_debtor(days_overdue=60, balance="5000.00"),
        make_debtor(days_overdue=90, balance="10.00"),
    )
    called = [call_now(client, auth_headers, agent["id"]).json()["debtor"]["id"] for _ in range(3)]
    assert called == [oldest.id, big.id, small.id]


def test_stats_and_history(client, auth_headers, create_agent, db_add, call_engine, clock):
    agent = create_agent()
    debtors = db_add(make_debtor(), make_debtor(), make_debtor())
    for outcome, days, amount in [
        (CallOutcome.PAYMENT_PROMISE, 5, "750.50"),
        (CallOutcome.REFUSED, None, None),
        (CallOutcome.NO_ANSWER, None, None),
    ]:
        call_engine.set(outcome, days, amount)
        assert call_now(client, auth_headers, agent["id"]).status_code == 201
        clock.advance(minutes=1)

    stats = client.get(f"/api/agents/{agent['id']}/stats", headers=auth_headers).json()
    assert stats == {
        "total": 3,
        "no_answer": 1,
        "payment_promise": 1,
        "refused": 1,
        "promised_amount_total": "750.50",
    }

    calls = client.get(f"/api/agents/{agent['id']}/calls", headers=auth_headers).json()
    assert [c["outcome"] for c in calls] == [
        "no_answer",
        "refused",
        "payment_promise",
    ]  # más reciente primero

    debtor_calls = client.get(f"/api/debtors/{debtors[0].id}/calls", headers=auth_headers).json()
    assert len(debtor_calls) == 1


def test_manual_call_works_while_paused_but_not_for_deleted_agent(client, auth_headers, create_agent, db_add):
    agent = create_agent()
    db_add(make_debtor())
    assert call_now(client, auth_headers, agent["id"]).status_code == 201
    client.delete(f"/api/agents/{agent['id']}", headers=auth_headers)
    assert call_now(client, auth_headers, agent["id"]).status_code == 404


def test_manual_call_with_simulated_engine(client, auth_headers, create_agent, db_add):
    app.dependency_overrides[get_call_engine] = lambda: SimulatedCallEngine(random.Random(1), answer_rate=1)
    agent = create_agent()
    db_add(make_debtor())

    body = call_now(client, auth_headers, agent["id"]).json()

    assert body["engine"] == "simulated"
    assert body["outcome"] in {"payment_promise", "refused"}
    assert body["transcript"][0]["text"].startswith("Llamando")
    assert {line["speaker"] for line in body["transcript"]} >= {"agent", "debtor"}
