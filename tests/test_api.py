from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_health_reports_provider():
    assert client.get("/health").json()["provider"] == "offline"


def test_customers_include_ledgers():
    customers = client.get("/api/customers").json()
    u001 = next(c for c in customers if c["user_id"] == "U001")
    assert {t["txn_id"] for t in u001["transactions"]} == {"TXN101", "TXN102", "TXN103"}


def test_review_returns_decision_and_clause():
    body = client.post("/api/review", json={"user_id": "u001", "message": "I got charged twice by Netflix"}).json()
    assert body["decision"] == "ESCALATE"
    assert body["policy_clause"] == "DUPLICATE-CHARGE-EXCEPTION"
    assert body["target_txn_ids"] == ["TXN101", "TXN102"]


def test_review_validates_input():
    assert client.post("/api/review", json={"user_id": "U001", "message": ""}).status_code == 422


def test_index_page_is_served():
    response = client.get("/")
    assert response.status_code == 200
    assert "Refund and fraud review agent" in response.text
