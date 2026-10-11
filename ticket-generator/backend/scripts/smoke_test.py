"""Verify live API and PostgreSQL, cleaning up only the ticket created here.

Run inside the backend container: python scripts/smoke_test.py
"""
import sys
from pathlib import Path
from uuid import uuid4
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import httpx
from sqlalchemy import func, select
from app.database.session import SessionLocal
from app.models import Ticket, User
from app.services.seed import seed


def main():
    ticket_id = None
    with httpx.Client(base_url="http://localhost:8001", timeout=10) as api:
        assert api.get("/api/health").json()["status"] == "ok"
        directory = api.get("/api/users").json()
        employees = [u for u in directory if u["role"] == "EMPLOYEE"]
        agents = [u for u in directory if u["role"] == "SUPPORT_AGENT"]
        employee, other = employees[:2]
        agent = agents[0]
        employee_headers = {"X-Demo-User-Id": str(employee["id"])}
        agent_headers = {"X-Demo-User-Id": str(agent["id"])}
        try:
            title = f"Smoke verification {uuid4().hex}"
            created = api.post("/api/tickets", headers=employee_headers, json={"title": title, "description": "Temporary API verification ticket", "category": "NETWORK", "created_by": employee["id"]})
            assert created.status_code == 201, created.text
            ticket = created.json()
            ticket_id = ticket["id"]
            path = f"/api/tickets/{ticket_id}"
            assert api.get(path, headers=employee_headers).json()["title"] == title
            assert api.get(path, headers={"X-Demo-User-Id": str(other["id"])}).status_code == 404
            assert api.patch(path, headers=employee_headers, json={"status": "CLOSED"}).status_code == 403
            changed = api.patch(path, headers=agent_headers, json={"status": "IN_PROGRESS", "priority": "HIGH", "assigned_to": agent["id"]})
            assert changed.status_code == 200, changed.text
            assert changed.json()["assignee"]["id"] == agent["id"]
            assert api.get("/api/tickets", headers=agent_headers, params={"search": title.lower(), "status": "IN_PROGRESS", "priority": "HIGH", "assigned_to": agent["id"]}).json()["total"] == 1
            assert api.post("/api/tickets", headers=employee_headers, json={"title": "  "}).status_code == 422
            with SessionLocal() as db:
                saved = db.get(Ticket, ticket_id)
                assert saved.title == title and saved.status.value == "IN_PROGRESS"
                counts_before = (db.scalar(select(func.count()).select_from(User)), db.scalar(select(func.count()).select_from(Ticket)))
            seed()
            seed()
            with SessionLocal() as db:
                counts_after = (db.scalar(select(func.count()).select_from(User)), db.scalar(select(func.count()).select_from(Ticket)))
            assert counts_before == counts_after
            print("PASS: live creation, PostgreSQL persistence, retrieval, filtering, updates, role restrictions, validation, and seed idempotence")
        finally:
            if ticket_id is not None:
                with SessionLocal.begin() as db:
                    temporary = db.get(Ticket, ticket_id)
                    if temporary is not None:
                        db.delete(temporary)


if __name__ == "__main__":
    main()
