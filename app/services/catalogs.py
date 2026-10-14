from app.domain.enums import (
    CURRENCY,
    PRODUCT_CATEGORY,
    AgentStatus,
    AgentType,
    CallOutcome,
    Country,
    NegotiationStyle,
    ProductType,
    label,
)
from app.schemas.catalog import Catalogs, CountryOption, Option, ProductOption


def _options(enum_cls) -> list[Option]:
    return [Option(value=member.value, label=label(member)) for member in enum_cls]


def build_catalogs() -> Catalogs:
    return Catalogs(
        countries=[CountryOption(value=c.value, label=label(c), currency=CURRENCY[c]) for c in Country],
        agent_types=_options(AgentType),
        product_types=[
            ProductOption(value=p.value, label=label(p), agent_type=PRODUCT_CATEGORY[p].value)
            for p in ProductType
        ],
        negotiation_styles=_options(NegotiationStyle),
        agent_statuses=_options(AgentStatus),
        call_outcomes=_options(CallOutcome),
    )
