from enum import StrEnum


class Country(StrEnum):
    AR = "AR"
    CL = "CL"
    CO = "CO"
    MX = "MX"
    US = "US"
    VE = "VE"
    PE = "PE"
    PY = "PY"


class AgentType(StrEnum):
    FINANCIAL = "financial"
    SERVICES = "services"


class ProductType(StrEnum):
    CREDIT_CARD = "credit_card"
    PERSONAL_LOAN = "personal_loan"
    MORTGAGE = "mortgage"
    MOBILE_PHONE = "mobile_phone"
    INTERNET = "internet"
    ELECTRICITY = "electricity"
    WATER = "water"
    GAS = "gas"


class NegotiationStyle(StrEnum):
    SOFT = "soft"
    FLEXIBLE = "flexible"
    STRICT = "strict"


class AgentStatus(StrEnum):
    PAUSED = "paused"
    ACTIVE = "active"


class CallOutcome(StrEnum):
    NO_ANSWER = "no_answer"
    PAYMENT_PROMISE = "payment_promise"
    REFUSED = "refused"


PRODUCT_CATEGORY: dict[ProductType, AgentType] = {
    ProductType.CREDIT_CARD: AgentType.FINANCIAL,
    ProductType.PERSONAL_LOAN: AgentType.FINANCIAL,
    ProductType.MORTGAGE: AgentType.FINANCIAL,
    ProductType.MOBILE_PHONE: AgentType.SERVICES,
    ProductType.INTERNET: AgentType.SERVICES,
    ProductType.ELECTRICITY: AgentType.SERVICES,
    ProductType.WATER: AgentType.SERVICES,
    ProductType.GAS: AgentType.SERVICES,
}

CURRENCY: dict[Country, str] = {
    Country.AR: "ARS",
    Country.CL: "CLP",
    Country.CO: "COP",
    Country.MX: "MXN",
    Country.US: "USD",
    Country.VE: "VES",
    Country.PE: "PEN",
    Country.PY: "PYG",
}

# Labels en español: solo los expone GET /catalogs
LABELS: dict[type[StrEnum], dict[str, str]] = {
    Country: {
        "AR": "Argentina",
        "CL": "Chile",
        "CO": "Colombia",
        "MX": "México",
        "US": "Estados Unidos",
        "VE": "Venezuela",
        "PE": "Perú",
        "PY": "Paraguay",
    },
    AgentType: {"financial": "Financiero", "services": "Servicios"},
    ProductType: {
        "credit_card": "Tarjeta de crédito",
        "personal_loan": "Préstamo personal",
        "mortgage": "Crédito hipotecario",
        "mobile_phone": "Telefonía móvil",
        "internet": "Internet",
        "electricity": "Electricidad",
        "water": "Agua",
        "gas": "Gas",
    },
    NegotiationStyle: {"soft": "Suave", "flexible": "Flexible", "strict": "Rígido"},
    AgentStatus: {"paused": "Pausado", "active": "Activo"},
    CallOutcome: {"no_answer": "No atendió", "payment_promise": "Promesa de pago", "refused": "No abonará"},
}


def label(value: StrEnum) -> str:
    return LABELS[type(value)][value.value]
