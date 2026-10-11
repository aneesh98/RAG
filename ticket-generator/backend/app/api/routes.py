from math import ceil
from fastapi import APIRouter, HTTPException, Query, Response
from sqlalchemy import func, or_, select, text
from sqlalchemy.orm import selectinload
from app.api.dependencies import DB, Identity
from app.models import Ticket, User, Role, Category, Priority, Status
from app.schemas.ticket import TicketCreate, TicketUpdate, TicketOut, TicketPage, TicketStats, UserOut, ErrorResponse

router = APIRouter(prefix="/api", responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}, 404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}})


def visible(user):
    query = select(Ticket)
    if user.role == Role.EMPLOYEE:
        query = query.where(Ticket.created_by == user.id)
    return query


def find_ticket(db, user, ticket_id):
    ticket = db.scalar(visible(user).where(Ticket.id == ticket_id).options(selectinload(Ticket.creator), selectinload(Ticket.assignee)))
    if ticket is None:
        raise HTTPException(404, "Ticket not found")
    return ticket


@router.get("/health", tags=["Health"])
def health(db: DB):
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        raise HTTPException(503, "Database unavailable")
    return {"status": "ok", "database": "ok"}


@router.get("/users", response_model=list[UserOut], tags=["Users"], description="Development-only account directory for the mock user selector.")
def users(db: DB):
    from app.core.config import settings
    if not settings.demo_auth_enabled:
        raise HTTPException(503, "Demo authentication is disabled")
    return db.scalars(select(User).order_by(User.id)).all()


@router.get("/tickets/stats", response_model=TicketStats, tags=["Tickets"])
def stats(db: DB, user: Identity):
    query = select(Ticket.status, func.count(Ticket.id)).group_by(Ticket.status)
    if user.role == Role.EMPLOYEE:
        query = query.where(Ticket.created_by == user.id)
    counts = dict(db.execute(query).all())
    return {"total": sum(counts.values()), "open": counts.get(Status.OPEN, 0), "in_progress": counts.get(Status.IN_PROGRESS, 0), "resolved": counts.get(Status.RESOLVED, 0), "closed": counts.get(Status.CLOSED, 0)}


@router.post("/tickets", response_model=TicketOut, status_code=201, tags=["Tickets"])
def create_ticket(body: TicketCreate, response: Response, db: DB, user: Identity):
    if user.role != Role.EMPLOYEE or body.created_by != user.id:
        raise HTTPException(403, "Employees may create tickets only for themselves")
    ticket = Ticket(**body.model_dump())
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    response.headers["Location"] = f"/api/tickets/{ticket.id}"
    return ticket


@router.get("/tickets", response_model=TicketPage, tags=["Tickets"])
def list_tickets(db: DB, user: Identity, status: Status | None = None, category: Category | None = None, priority: Priority | None = None, created_by: int | None = Query(None, gt=0), assigned_to: int | None = Query(None, gt=0), search: str | None = Query(None, max_length=200), page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100)):
    query = visible(user)
    for field, value in ((Ticket.status, status), (Ticket.category, category), (Ticket.priority, priority), (Ticket.created_by, created_by), (Ticket.assigned_to, assigned_to)):
        if value is not None:
            query = query.where(field == value)
    if search and search.strip():
        escaped = search.strip().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        pattern = f"%{escaped}%"
        query = query.where(or_(Ticket.title.ilike(pattern, escape="\\"), Ticket.description.ilike(pattern, escape="\\")))
    total = db.scalar(select(func.count()).select_from(query.subquery()))
    items = db.scalars(query.options(selectinload(Ticket.creator), selectinload(Ticket.assignee)).order_by(Ticket.created_at.desc(), Ticket.id.desc()).offset((page - 1) * page_size).limit(page_size)).all()
    return {"items": items, "total": total, "page": page, "page_size": page_size, "total_pages": ceil(total / page_size)}


@router.get("/tickets/{ticket_id}", response_model=TicketOut, tags=["Tickets"])
def get_ticket(ticket_id: int, db: DB, user: Identity):
    return find_ticket(db, user, ticket_id)


@router.patch("/tickets/{ticket_id}", response_model=TicketOut, tags=["Tickets"])
def update_ticket(ticket_id: int, body: TicketUpdate, db: DB, user: Identity):
    if user.role != Role.SUPPORT_AGENT:
        raise HTTPException(403, "Only support agents may manage tickets")
    ticket = find_ticket(db, user, ticket_id)
    changes = body.model_dump(exclude_unset=True)
    if changes.get("assigned_to") is not None:
        agent = db.get(User, changes["assigned_to"])
        if agent is None or agent.role != Role.SUPPORT_AGENT:
            raise HTTPException(422, "assigned_to must reference a support agent")
    for field, value in changes.items():
        setattr(ticket, field, value)
    from app.models.ticket import utcnow
    ticket.updated_at = utcnow()
    db.commit()
    db.refresh(ticket)
    return ticket
