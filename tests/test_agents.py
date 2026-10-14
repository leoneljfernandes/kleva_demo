import pytest

from tests.conftest import AGENT_PAYLOAD


def test_agents_require_auth(client):
    assert client.get("/api/agents").status_code == 401
    assert client.post("/api/agents", json=AGENT_PAYLOAD).status_code == 401


def test_create_agent_starts_paused(create_agent):
    agent = create_agent()
    assert agent["status"] == "paused"
    assert {k: agent[k] for k in AGENT_PAYLOAD} == AGENT_PAYLOAD


def test_create_rejects_product_from_other_category(client, auth_headers):
    payload = {**AGENT_PAYLOAD, "agent_type": "services"}  # credit_card es financiero
    response = client.post("/api/agents", json=payload, headers=auth_headers)
    assert response.status_code == 422


@pytest.mark.parametrize(
    "field, value",
    [
        ("name", "   "),
        ("min_days_overdue", -1),
        ("country", "BR"),
        ("negotiation_style", "aggressive"),
        ("product_type", "insurance"),
        ("agent_type", None),
    ],
)
def test_create_rejects_invalid_fields(client, auth_headers, field, value):
    response = client.post("/api/agents", json={**AGENT_PAYLOAD, field: value}, headers=auth_headers)
    assert response.status_code == 422
    assert field in response.json()["detail"][0]["loc"]


def test_list_and_get_agents(client, auth_headers, create_agent):
    first = create_agent()
    second = create_agent(name="Mateo", country="MX")
    listed = client.get("/api/agents", headers=auth_headers).json()
    assert [a["id"] for a in listed] == [first["id"], second["id"]]
    assert client.get(f"/api/agents/{second['id']}", headers=auth_headers).json()["name"] == "Mateo"


def test_get_unknown_agent(client, auth_headers):
    assert client.get("/api/agents/999", headers=auth_headers).status_code == 404


def test_update_paused_agent(client, auth_headers, create_agent):
    agent = create_agent()
    response = client.patch(
        f"/api/agents/{agent['id']}",
        json={"negotiation_style": "strict", "min_days_overdue": 60},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["negotiation_style"] == "strict"
    assert response.json()["min_days_overdue"] == 60
    assert response.json()["name"] == "Valeria"


def test_update_validates_category_against_merged_agent(client, auth_headers, create_agent):
    agent = create_agent()  # financial + credit_card
    response = client.patch(
        f"/api/agents/{agent['id']}", json={"agent_type": "services"}, headers=auth_headers
    )
    assert response.status_code == 422
    response = client.patch(
        f"/api/agents/{agent['id']}",
        json={"agent_type": "services", "product_type": "internet"},
        headers=auth_headers,
    )
    assert response.status_code == 200


def test_active_agent_cannot_be_updated_or_deleted(client, auth_headers, create_agent):
    agent = create_agent()
    client.post(f"/api/agents/{agent['id']}/start", headers=auth_headers)
    patch = client.patch(f"/api/agents/{agent['id']}", json={"name": "Otro"}, headers=auth_headers)
    delete = client.delete(f"/api/agents/{agent['id']}", headers=auth_headers)
    assert patch.status_code == 409
    assert delete.status_code == 409


def test_delete_is_soft(client, auth_headers, create_agent):
    agent = create_agent()
    assert client.delete(f"/api/agents/{agent['id']}", headers=auth_headers).status_code == 204
    assert client.get(f"/api/agents/{agent['id']}", headers=auth_headers).status_code == 404
    assert client.get("/api/agents", headers=auth_headers).json() == []
    assert client.post(f"/api/agents/{agent['id']}/start", headers=auth_headers).status_code == 404


def test_start_and_pause_are_idempotent(client, auth_headers, create_agent):
    agent = create_agent()
    for _ in range(2):
        response = client.post(f"/api/agents/{agent['id']}/start", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "active"
    for _ in range(2):
        response = client.post(f"/api/agents/{agent['id']}/pause", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "paused"
