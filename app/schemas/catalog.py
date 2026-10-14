from pydantic import BaseModel


class Option(BaseModel):
    value: str
    label: str


class CountryOption(Option):
    currency: str


class ProductOption(Option):
    agent_type: str


class Catalogs(BaseModel):
    countries: list[CountryOption]
    agent_types: list[Option]
    product_types: list[ProductOption]
    negotiation_styles: list[Option]
    agent_statuses: list[Option]
    call_outcomes: list[Option]
