from sqlalchemy import func, select
from app.main import app
from app.models import Ticket, User, Status
from app.services import seed as seed_module


def test_seed_is_idempotent_and_preserves_updates(client, monkeypatch):
    monkeypatch.setattr(seed_module, "SessionLocal", app.state.test_sessions)
    seed_module.seed()
    with app.state.test_sessions.begin() as db:
        users_before = db.scalar(select(func.count()).select_from(User))
        tickets_before = db.scalar(select(func.count()).select_from(Ticket))
        ticket = db.scalar(select(Ticket).where(Ticket.title == "Laptop display flickers"))
        ticket_id = ticket.id
        ticket.status = Status.RESOLVED
    seed_module.seed()
    with app.state.test_sessions() as db:
        assert db.scalar(select(func.count()).select_from(User)) == users_before
        assert db.scalar(select(func.count()).select_from(Ticket)) == tickets_before == 10
        assert db.get(Ticket, ticket_id).status == Status.RESOLVED
