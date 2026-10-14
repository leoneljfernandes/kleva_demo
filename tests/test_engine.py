"""Tests unitarios del engine simulado: lógica pura sin I/O (excepción justificada a la regla E2E)."""

import asyncio
import random
from decimal import Decimal

import pytest

from app.domain.enums import CallOutcome, Country, NegotiationStyle, ProductType
from app.services.call_engine.base import AgentSnapshot, CallResult, DebtorSnapshot
from app.services.call_engine.simulated import STYLE_PROFILES, SimulatedCallEngine

N = 2000


def make_agent(
    style: NegotiationStyle = NegotiationStyle.SOFT, country: Country = Country.AR
) -> AgentSnapshot:
    return AgentSnapshot(id=1, name="Valeria", country=country, negotiation_style=style)


def make_debtor(days: int = 45, balance: str = "150000.00", country: Country = Country.AR) -> DebtorSnapshot:
    return DebtorSnapshot(
        id=1,
        first_name="Juan",
        country=country,
        product_type=ProductType.CREDIT_CARD,
        balance=Decimal(balance),
        days_overdue=days,
    )


def run_many(
    engine: SimulatedCallEngine, agent: AgentSnapshot, debtor: DebtorSnapshot, n: int
) -> list[CallResult]:
    async def _many():
        return [await engine.run(agent, debtor) for _ in range(n)]

    return asyncio.run(_many())


def rate(results: list[CallResult], outcome: CallOutcome) -> float:
    return sum(r.outcome == outcome for r in results) / len(results)


def test_same_seed_reproduces_same_results():
    first = run_many(SimulatedCallEngine(random.Random(7)), make_agent(), make_debtor(), 50)
    second = run_many(SimulatedCallEngine(random.Random(7)), make_agent(), make_debtor(), 50)
    assert first == second


def test_promise_rate_is_ordered_by_style():
    rates = {
        style: rate(
            run_many(SimulatedCallEngine(random.Random(1)), make_agent(style), make_debtor(), N),
            CallOutcome.PAYMENT_PROMISE,
        )
        for style in NegotiationStyle
    }
    assert rates[NegotiationStyle.STRICT] < rates[NegotiationStyle.FLEXIBLE] < rates[NegotiationStyle.SOFT]


@pytest.mark.parametrize("style", list(NegotiationStyle))
def test_answer_rate_does_not_depend_on_style(style):
    results = run_many(
        SimulatedCallEngine(random.Random(3), answer_rate=0.65), make_agent(style), make_debtor(), N
    )
    assert rate(results, CallOutcome.NO_ANSWER) == pytest.approx(0.35, abs=0.04)


@pytest.mark.parametrize("style", list(NegotiationStyle))
def test_promise_fields_respect_style_profile(style):
    profile = STYLE_PROFILES[style]
    debtor = make_debtor()
    results = run_many(SimulatedCallEngine(random.Random(5)), make_agent(style), debtor, 500)
    for r in results:
        if r.outcome is CallOutcome.PAYMENT_PROMISE:
            assert profile.promise_days[0] <= r.promised_days <= profile.promise_days[1]
            min_amount = debtor.balance * (1 - Decimal(profile.discount_pct[1]) / 100)
            assert min_amount <= r.promised_amount <= debtor.balance
        else:
            assert r.promised_days is None
            assert r.promised_amount is None


def test_old_debt_lowers_promise_rate():
    engine_args = (make_agent(NegotiationStyle.SOFT),)
    recent = run_many(SimulatedCallEngine(random.Random(9)), *engine_args, make_debtor(days=30), N)
    old = run_many(SimulatedCallEngine(random.Random(9)), *engine_args, make_debtor(days=120), N)
    assert rate(old, CallOutcome.PAYMENT_PROMISE) < rate(recent, CallOutcome.PAYMENT_PROMISE)


def test_never_answers_with_zero_answer_rate():
    results = run_many(SimulatedCallEngine(random.Random(1), answer_rate=0), make_agent(), make_debtor(), 100)
    assert {r.outcome for r in results} == {CallOutcome.NO_ANSWER}
    assert all(line.speaker == "system" for r in results for line in r.transcript)


def test_answered_call_has_dialogue_and_engine_name():
    [result] = run_many(SimulatedCallEngine(random.Random(1), answer_rate=1), make_agent(), make_debtor(), 1)
    speakers = {line.speaker for line in result.transcript}
    assert {"agent", "debtor"} <= speakers
    assert result.engine == "simulated"
    assert result.duration_seconds > 0


def test_transcript_is_in_english_for_us():
    [us] = run_many(
        SimulatedCallEngine(random.Random(1), answer_rate=1),
        make_agent(country=Country.US),
        make_debtor(country=Country.US, balance="900.00"),
        1,
    )
    [ar] = run_many(SimulatedCallEngine(random.Random(1), answer_rate=1), make_agent(), make_debtor(), 1)
    assert us.transcript[0].text.startswith("Calling")
    assert ar.transcript[0].text.startswith("Llamando")
    assert any("USD" in line.text for line in us.transcript)
    assert any("ARS" in line.text for line in ar.transcript)
