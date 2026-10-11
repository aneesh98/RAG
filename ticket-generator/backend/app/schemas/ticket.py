from datetime import datetime, timezone
from pydantic import BaseModel, ConfigDict, Field, field_serializer, model_validator
from app.models import Category, Priority, Status, Role


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: Role
    model_config = ConfigDict(from_attributes=True)


class TicketCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=20000)
    category: Category
    priority: Priority = Priority.MEDIUM
    created_by: int = Field(gt=0)
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class TicketUpdate(BaseModel):
    status: Status | None = None
    priority: Priority | None = None
    assigned_to: int | None = Field(default=None, gt=0)
    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_changes(self):
        if not self.model_fields_set:
            raise ValueError("At least one management field is required")
        for field in ("status", "priority"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        return self


class TicketOut(BaseModel):
    id: int
    title: str
    description: str
    category: Category
    priority: Priority
    status: Status
    created_by: int
    assigned_to: int | None
    created_at: datetime
    updated_at: datetime
    creator: UserOut
    assignee: UserOut | None
    model_config = ConfigDict(from_attributes=True)

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, value: datetime):
        return value.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z") if value.tzinfo is None else value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


class TicketPage(BaseModel):
    items: list[TicketOut]
    total: int
    page: int
    page_size: int
    total_pages: int


class TicketStats(BaseModel):
    total: int
    open: int
    in_progress: int
    resolved: int
    closed: int


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: list[dict] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    error: ErrorDetail
