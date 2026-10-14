"""Frases de la llamada emulada por idioma y estilo. Solo texto: ninguna decisión vive acá."""

import random
from dataclasses import dataclass
from decimal import Decimal

from app.domain.enums import CURRENCY, LABELS, Country, NegotiationStyle, ProductType
from app.services.call_engine.base import AgentSnapshot, DebtorSnapshot, TranscriptLine

Style = NegotiationStyle

EN_PRODUCTS = {
    ProductType.CREDIT_CARD: "credit card",
    ProductType.PERSONAL_LOAN: "personal loan",
    ProductType.MORTGAGE: "mortgage",
    ProductType.MOBILE_PHONE: "mobile phone plan",
    ProductType.INTERNET: "internet service",
    ProductType.ELECTRICITY: "electricity service",
    ProductType.WATER: "water service",
    ProductType.GAS: "gas service",
}

PHRASES: dict[str, dict] = {
    "es": {
        "dialing": ["Llamando a {name}…"],
        "no_answer": [
            "No atendió. Se reintentará más tarde.",
            "Buzón de voz. No se dejó mensaje.",
            "Sonó hasta cortar. Sin respuesta.",
        ],
        "greeting": [
            "Hola {name}, te habla {agent} de Kleva. Te llamo por tu deuda de {product}.",
            "Buen día {name}, soy {agent} y te llamo por tu deuda de {product}.",
        ],
        "pickup": ["Sí, ¿quién habla?", "Hola, sí, decime.", "¿Qué necesitás?"],
        "situation": ["Registramos un saldo pendiente de {amount}, con {days} días de atraso."],
        "offer": {
            Style.SOFT: [
                "Entendemos que puede ser un momento difícil. Podemos armar un plan en cuotas "
                "sin recargo, a tu ritmo."
            ],
            Style.FLEXIBLE: [
                "Si regularizás en los próximos días, podemos aplicarte una quita de hasta "
                "el 30% sobre el saldo."
            ],
            Style.STRICT: [
                "Necesitamos el pago total del saldo a la brevedad. De lo contrario, la deuda "
                "pasa a gestión prejudicial."
            ],
        },
        "promise_debtor": [
            "Está bien, puedo pagar {amount} en {days} días.",
            "Ok, en {days} días te abono {amount}.",
        ],
        "discount": ["Con la quita del {pct}% el saldo queda en {amount}."],
        "promise_agent": ["Perfecto, queda registrada tu promesa de pago a {days} días. ¡Gracias, {name}!"],
        "refusal_debtor": [
            "No voy a poder pagar.",
            "No reconozco esa deuda.",
            "Ahora no tengo cómo, no me llamen más.",
        ],
        "refusal_agent": {
            Style.SOFT: ["Entiendo. Te volvemos a contactar más adelante para buscar una alternativa."],
            Style.FLEXIBLE: ["Entiendo. La propuesta de quita queda disponible si cambiás de opinión."],
            Style.STRICT: ["Entendido. Dejamos constancia de la negativa y el caso sigue su curso."],
        },
    },
    "en": {
        "dialing": ["Calling {name}…"],
        "no_answer": [
            "No answer. Will retry later.",
            "Voicemail. No message left.",
            "Rang out. No response.",
        ],
        "greeting": [
            "Hello {name}, this is {agent} from Kleva, calling about your {product}.",
            "Good morning {name}, I'm {agent} and I'm calling about your {product}.",
        ],
        "pickup": ["Yes, who is this?", "Hi, go ahead.", "What do you need?"],
        "situation": ["We show an outstanding balance of {amount}, {days} days past due."],
        "offer": {
            Style.SOFT: [
                "We understand this may be a hard time. We can set up an installment plan with no extra fees."
            ],
            Style.FLEXIBLE: ["If you settle in the next few days, we can take up to 30% off the balance."],
            Style.STRICT: [
                "We need the full balance paid promptly. Otherwise the account moves to pre-legal collection."
            ],
        },
        "promise_debtor": [
            "Alright, I can pay {amount} in {days} days.",
            "Ok, I'll pay {amount} in {days} days.",
        ],
        "discount": ["With the {pct}% discount the balance comes to {amount}."],
        "promise_agent": ["Great, your payment promise in {days} days is on record. Thank you, {name}!"],
        "refusal_debtor": [
            "I can't pay.",
            "I don't recognize this debt.",
            "I can't right now, stop calling.",
        ],
        "refusal_agent": {
            Style.SOFT: ["I understand. We'll reach out later to find an alternative."],
            Style.FLEXIBLE: ["Understood. The discount offer stays open if you change your mind."],
            Style.STRICT: ["Understood. The refusal is on record and the case will proceed."],
        },
    },
}


def format_money(amount: Decimal, currency: str, lang: str) -> str:
    text = f"{amount:,.2f}"  # 1,234.50
    if lang == "es":
        text = text.replace(",", "_").replace(".", ",").replace("_", ".")  # 1.234,50
    return f"{currency} {text}"


@dataclass
class Script:
    lang: str
    currency: str
    rng: random.Random

    def _pick(self, key: str, style: NegotiationStyle | None = None, **fmt) -> str:
        options = PHRASES[self.lang][key]
        if style is not None:
            options = options[style]
        return self.rng.choice(options).format(**fmt)

    def _money(self, amount: Decimal) -> str:
        return format_money(amount, self.currency, self.lang)

    def _product(self, product: ProductType) -> str:
        return EN_PRODUCTS[product] if self.lang == "en" else LABELS[ProductType][product].lower()

    def dialing(self, debtor: DebtorSnapshot) -> TranscriptLine:
        return TranscriptLine("system", self._pick("dialing", name=debtor.first_name))

    def no_answer(self) -> TranscriptLine:
        return TranscriptLine("system", self._pick("no_answer"))

    def opening(self, agent: AgentSnapshot, debtor: DebtorSnapshot) -> list[TranscriptLine]:
        return [
            TranscriptLine("debtor", self._pick("pickup")),
            TranscriptLine(
                "agent",
                self._pick(
                    "greeting",
                    name=debtor.first_name,
                    agent=agent.name,
                    product=self._product(debtor.product_type),
                ),
            ),
            TranscriptLine(
                "agent", self._pick("situation", amount=self._money(debtor.balance), days=debtor.days_overdue)
            ),
        ]

    def offer(self, style: NegotiationStyle) -> list[TranscriptLine]:
        return [TranscriptLine("agent", self._pick("offer", style))]

    def promise(
        self, debtor: DebtorSnapshot, days: int, amount: Decimal, discount_pct: int
    ) -> list[TranscriptLine]:
        lines = []
        if discount_pct:
            lines.append(
                TranscriptLine("agent", self._pick("discount", pct=discount_pct, amount=self._money(amount)))
            )
        lines.append(
            TranscriptLine("debtor", self._pick("promise_debtor", amount=self._money(amount), days=days))
        )
        lines.append(TranscriptLine("agent", self._pick("promise_agent", days=days, name=debtor.first_name)))
        return lines

    def refusal(self, style: NegotiationStyle) -> list[TranscriptLine]:
        return [
            TranscriptLine("debtor", self._pick("refusal_debtor")),
            TranscriptLine("agent", self._pick("refusal_agent", style)),
        ]


def for_country(country: Country, rng: random.Random) -> Script:
    return Script(lang="en" if country is Country.US else "es", currency=CURRENCY[country], rng=rng)
