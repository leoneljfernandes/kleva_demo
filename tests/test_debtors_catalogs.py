from app.domain.enums import Country, ProductType
from tests.conftest import make_debtor


def test_list_debtors_with_filters(client, auth_headers, db_add):
    db_add(
        make_debtor(days_overdue=10),
        make_debtor(days_overdue=120),
        make_debtor(country=Country.PE, product_type=ProductType.WATER, days_overdue=80),
    )
    all_debtors = client.get("/api/debtors", headers=auth_headers).json()
    assert [d["days_overdue"] for d in all_debtors] == [120, 80, 10]

    filtered = client.get(
        "/api/debtors", params={"country": "AR", "min_days_overdue": 30}, headers=auth_headers
    ).json()
    assert [d["days_overdue"] for d in filtered] == [120]
    assert filtered[0]["balance"] == "1000.00"


def test_get_unknown_debtor(client, auth_headers):
    assert client.get("/api/debtors/999", headers=auth_headers).status_code == 404
    assert client.get("/api/debtors/999/calls", headers=auth_headers).status_code == 404


def test_debtors_require_auth(client):
    assert client.get("/api/debtors").status_code == 401


def test_catalogs_expose_enums_with_labels(client, auth_headers):
    catalogs = client.get("/api/catalogs", headers=auth_headers).json()
    assert {"value": "AR", "label": "Argentina", "currency": "ARS"} in catalogs["countries"]
    assert len(catalogs["countries"]) == 8
    assert {"value": "strict", "label": "Rígido"} in catalogs["negotiation_styles"]
    credit_card = next(p for p in catalogs["product_types"] if p["value"] == "credit_card")
    assert credit_card["agent_type"] == "financial"
    assert {o["value"] for o in catalogs["call_outcomes"]} == {"no_answer", "payment_promise", "refused"}
