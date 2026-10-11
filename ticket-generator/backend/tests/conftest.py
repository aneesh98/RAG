import os
os.environ.setdefault("DATABASE_URL", "sqlite://")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database.session import Base, get_db
from app.main import app
from app.models import User, Role


@pytest.fixture()
def client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, record):
        connection.execute("PRAGMA foreign_keys=ON")
    Base.metadata.create_all(engine)
    sessions = sessionmaker(bind=engine, expire_on_commit=False)
    with sessions.begin() as db:
        db.add_all([
            User(id=1, name="Employee One", email="one@example.com", role=Role.EMPLOYEE),
            User(id=2, name="Employee Two", email="two@example.com", role=Role.EMPLOYEE),
            User(id=4, name="Agent One", email="agent@example.com", role=Role.SUPPORT_AGENT),
            User(id=5, name="Agent Two", email="agent2@example.com", role=Role.SUPPORT_AGENT),
        ])
    def override():
        with sessions() as db:
            yield db
    app.dependency_overrides[get_db] = override
    app.state.test_sessions = sessions
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    engine.dispose()
