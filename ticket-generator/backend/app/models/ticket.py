import enum
from datetime import datetime, timezone
from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.session import Base


class Role(str, enum.Enum):
    EMPLOYEE = "EMPLOYEE"
    SUPPORT_AGENT = "SUPPORT_AGENT"


class Category(str, enum.Enum):
    HARDWARE = "HARDWARE"
    SOFTWARE = "SOFTWARE"
    NETWORK = "NETWORK"
    ACCESS = "ACCESS"
    OTHER = "OTHER"


class Priority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Status(str, enum.Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


def utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(254), unique=True)
    role: Mapped[Role] = mapped_column(Enum(Role, name="user_role", create_constraint=True))


class Ticket(Base):
    __tablename__ = "tickets"
    __table_args__ = (
        CheckConstraint("length(trim(title)) > 0", name="ticket_title_nonempty"),
        CheckConstraint("length(trim(description)) > 0", name="ticket_description_nonempty"),
        Index("ix_tickets_created_at", "created_at"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    category: Mapped[Category] = mapped_column(Enum(Category, name="ticket_category", create_constraint=True), index=True)
    priority: Mapped[Priority] = mapped_column(Enum(Priority, name="ticket_priority", create_constraint=True), default=Priority.MEDIUM, server_default="MEDIUM", index=True)
    status: Mapped[Status] = mapped_column(Enum(Status, name="ticket_status", create_constraint=True), default=Status.OPEN, server_default="OPEN", index=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True)
    assigned_to: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    creator: Mapped[User] = relationship(foreign_keys=[created_by])
    assignee: Mapped[User | None] = relationship(foreign_keys=[assigned_to])
