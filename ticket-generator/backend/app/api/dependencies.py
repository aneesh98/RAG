from typing import Annotated
from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session
from app.core.config import settings
from app.database.session import get_db
from app.models import User

DB = Annotated[Session, Depends(get_db)]


def current_user(db: DB, x_demo_user_id: Annotated[int | None, Header(description="DEVELOPMENT ONLY: impersonate a seeded user. This is not secure authentication.", gt=0)] = None):
    if not settings.demo_auth_enabled:
        raise HTTPException(503, "Mock authentication disabled; no production authentication is configured")
    if x_demo_user_id is None:
        raise HTTPException(401, "X-Demo-User-Id header is required")
    user = db.get(User, x_demo_user_id)
    if user is None:
        raise HTTPException(401, "Unknown demo user")
    return user


Identity = Annotated[User, Depends(current_user)]
