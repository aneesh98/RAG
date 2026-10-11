import pytest

EMPLOYEE = {"X-Demo-User-Id": "1"}
OTHER = {"X-Demo-User-Id": "2"}
AGENT = {"X-Demo-User-Id": "4"}
BODY = {"title": "Laptop broken", "description": "The DISPLAY is flickering", "category": "HARDWARE", "created_by": 1}


def create(client, **changes):
    response = client.post("/api/tickets", headers=EMPLOYEE, json={**BODY, **changes})
    assert response.status_code == 201
    return response.json()


def test_creation_defaults_and_retrieval(client):
    ticket = create(client)
    assert ticket["id"] > 0
    assert ticket["priority"] == "MEDIUM"
    assert ticket["status"] == "OPEN"
    assert ticket["assigned_to"] is None
    assert ticket["created_at"].endswith("Z")
    assert ticket["updated_at"] == ticket["created_at"] or ticket["updated_at"] >= ticket["created_at"]
    assert ticket["creator"]["id"] == 1
    assert client.get(f'/api/tickets/{ticket["id"]}', headers=EMPLOYEE).json() == ticket


@pytest.mark.parametrize("changes", [
    {"title": ""}, {"title": "   "}, {"description": "\n  "}, {"title": "x" * 201},
    {"category": "INVALID"}, {"priority": "URGENT"}, {"created_by": 0}, {"status": "CLOSED"},
])
def test_invalid_creation(client, changes):
    response = client.post("/api/tickets", headers=EMPLOYEE, json={**BODY, **changes})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_missing_required_fields(client):
    assert client.post("/api/tickets", headers=EMPLOYEE, json={}).status_code == 422


def test_not_found_and_employee_scope(client):
    ticket = create(client)
    assert client.get("/api/tickets/999", headers=EMPLOYEE).status_code == 404
    assert client.get(f'/api/tickets/{ticket["id"]}', headers=OTHER).status_code == 404
    assert client.get("/api/tickets", headers=OTHER).json()["total"] == 0
    assert client.get("/api/tickets?created_by=1", headers=OTHER).json()["total"] == 0
    assert client.get("/api/tickets", headers=AGENT).json()["total"] == 1


def test_filters_search_and_pagination(client):
    first = create(client)
    create(client, title="VPN failure", description="Cannot connect remotely", category="NETWORK", priority="HIGH")
    client.patch(f'/api/tickets/{first["id"]}', headers=AGENT, json={"status": "IN_PROGRESS", "assigned_to": 4})
    for query in ("category=HARDWARE", "status=IN_PROGRESS", "priority=MEDIUM", "created_by=1&category=HARDWARE", "assigned_to=4", "search=display", "search=LAPTOP"):
        data = client.get(f"/api/tickets?{query}", headers=EMPLOYEE).json()
        assert data["total"] == 1
        assert data["items"][0]["id"] == first["id"]
    data = client.get("/api/tickets?page=1&page_size=1", headers=EMPLOYEE).json()
    assert data["total"] == 2 and data["total_pages"] == 2 and len(data["items"]) == 1
    assert client.get("/api/tickets?page=2&page_size=1", headers=EMPLOYEE).json()["items"][0]["id"] != data["items"][0]["id"]
    assert client.get("/api/tickets?search=%25", headers=EMPLOYEE).json()["total"] == 0


@pytest.mark.parametrize("query", ["page=0", "page_size=101", "status=BAD", "assigned_to=-1", "category=BAD", "priority=BAD"])
def test_invalid_filters(client, query):
    assert client.get(f"/api/tickets?{query}", headers=EMPLOYEE).status_code == 422


def test_agent_updates_and_unassignment(client):
    ticket = create(client)
    response = client.patch(f'/api/tickets/{ticket["id"]}', headers=AGENT, json={"status": "RESOLVED", "priority": "CRITICAL", "assigned_to": 4})
    assert response.status_code == 200
    updated = response.json()
    assert updated["status"] == "RESOLVED" and updated["priority"] == "CRITICAL"
    assert updated["assignee"]["id"] == 4
    assert updated["created_at"] == ticket["created_at"]
    assert updated["updated_at"] > ticket["updated_at"]
    reassigned = client.patch(f'/api/tickets/{ticket["id"]}', headers=AGENT, json={"assigned_to": 5}).json()
    assert reassigned["assignee"]["id"] == 5
    unassigned = client.patch(f'/api/tickets/{ticket["id"]}', headers=AGENT, json={"assigned_to": None}).json()
    assert unassigned["assigned_to"] is None and unassigned["assignee"] is None


@pytest.mark.parametrize("body", [{}, {"status": None}, {"priority": None}, {"status": "BAD"}, {"assigned_to": 1}, {"assigned_to": 999}, {"created_by": 2}, {"title": "changed"}])
def test_invalid_updates(client, body):
    ticket = create(client)
    assert client.patch(f'/api/tickets/{ticket["id"]}', headers=AGENT, json=body).status_code == 422


def test_role_restrictions(client):
    ticket = create(client)
    for body in ({"status": "CLOSED"}, {"priority": "LOW"}, {"assigned_to": 4}):
        assert client.patch(f'/api/tickets/{ticket["id"]}', headers=EMPLOYEE, json=body).status_code == 403
    assert client.post("/api/tickets", headers=EMPLOYEE, json={**BODY, "created_by": 2}).status_code == 403
    assert client.post("/api/tickets", headers=AGENT, json=BODY).status_code == 403
    assert client.patch("/api/tickets/999", headers=AGENT, json={"status": "CLOSED"}).status_code == 404


def test_identity_and_health(client):
    assert client.get("/api/health").json() == {"status": "ok", "database": "ok"}
    assert len(client.get("/api/users").json()) == 4
    assert client.get("/api/tickets").status_code == 401
    assert client.get("/api/tickets", headers={"X-Demo-User-Id": "999"}).status_code == 401
    assert client.get("/api/tickets", headers={"X-Demo-User-Id": "abc"}).status_code == 422


def test_statistics_scope(client):
    create(client)
    client.post("/api/tickets", headers=OTHER, json={**BODY, "created_by": 2})
    own = client.get("/api/tickets/stats", headers=EMPLOYEE).json()
    assert own == {"total": 1, "open": 1, "in_progress": 0, "resolved": 0, "closed": 0}
    assert client.get("/api/tickets/stats", headers=AGENT).json()["total"] == 2


def test_demo_auth_can_be_disabled(client, monkeypatch):
    from app.core.config import settings
    monkeypatch.setattr(settings, "demo_auth_enabled", False)
    assert client.get("/api/tickets", headers=EMPLOYEE).status_code == 503
    assert client.get("/api/users").status_code == 503
