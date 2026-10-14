"""Emulación de la llamada: dos sorteos independientes (¿atiende? y, si atiende, ¿qué decide?)."""

import random
from dataclasses import dataclass
from decimal import Decimal

from app.domain.enums import CallOutcome, NegotiationStyle
from app.services.call_engine import scripts
from app.services.call_engine.base import AgentSnapshot, CallResult, DebtorSnapshot

OLD_DEBT_DAYS = 90
OLD_DEBT_PENALTY = 0.15
MIN_PROMISE_PROBABILITY = 0.05


@dataclass(frozen=True)
class StyleProfile:
    promise_probability: float
    promise_days: tuple[int, int]
    discount_pct: tuple[int, int]  # enteros: evita floats en dinero


STYLE_PROFILES: dict[NegotiationStyle, StyleProfile] = {
    NegotiationStyle.SOFT: StyleProfile(0.70, (15, 30), (0, 0)),
    NegotiationStyle.FLEXIBLE: StyleProfile(0.55, (7, 15), (10, 30)),
    NegotiationStyle.STRICT: StyleProfile(0.40, (1, 5), (0, 0)),
}


class SimulatedCallEngine:
    name = "simulated"

    def __init__(self, rng: random.Random, answer_rate: float = 0.65):
        self.rng = rng
        self.answer_rate = answer_rate

    async def run(self, agent: AgentSnapshot, debtor: DebtorSnapshot) -> CallResult:
        script = scripts.for_country(agent.country, self.rng)
        lines = [script.dialing(debtor)]

        # 1) ¿Atiende? No depende del estilo: el estilo no hace que levante el teléfono
        if self.rng.random() >= self.answer_rate:
            lines.append(script.no_answer())
            return CallResult(CallOutcome.NO_ANSWER, self.rng.randint(15, 40), lines, self.name)

        # 2) ¿Qué decide? Perfil del estilo, penalizado si la deuda es vieja
        profile = STYLE_PROFILES[agent.negotiation_style]
        penalty = OLD_DEBT_PENALTY if debtor.days_overdue > OLD_DEBT_DAYS else 0.0
        p_promise = max(MIN_PROMISE_PROBABILITY, profile.promise_probability - penalty)
        lines += script.opening(agent, debtor)
        lines += script.offer(agent.negotiation_style)

        if self.rng.random() < p_promise:
            days = self.rng.randint(*profile.promise_days)
            discount_pct = self.rng.randint(*profile.discount_pct)
            amount = (debtor.balance * (1 - Decimal(discount_pct) / 100)).quantize(Decimal("0.01"))
            lines += script.promise(debtor, days, amount, discount_pct)
            return CallResult(
                CallOutcome.PAYMENT_PROMISE,
                self.rng.randint(90, 300),
                lines,
                self.name,
                promised_days=days,
                promised_amount=amount,
            )

        lines += script.refusal(agent.negotiation_style)
        return CallResult(CallOutcome.REFUSED, self.rng.randint(60, 240), lines, self.name)
