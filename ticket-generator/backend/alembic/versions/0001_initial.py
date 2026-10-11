"""Create users and tickets with enums, constraints, foreign keys and indexes."""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("email", sa.String(254), nullable=False, unique=True),
        sa.Column("role", sa.Enum("EMPLOYEE", "SUPPORT_AGENT", name="user_role", create_constraint=True), nullable=False))
    op.create_table("tickets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("category", sa.Enum("HARDWARE", "SOFTWARE", "NETWORK", "ACCESS", "OTHER", name="ticket_category", create_constraint=True), nullable=False),
        sa.Column("priority", sa.Enum("LOW", "MEDIUM", "HIGH", "CRITICAL", name="ticket_priority", create_constraint=True), nullable=False, server_default="MEDIUM"),
        sa.Column("status", sa.Enum("OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED", name="ticket_status", create_constraint=True), nullable=False, server_default="OPEN"),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("assigned_to", sa.Integer(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("length(trim(title)) > 0", name="ticket_title_nonempty"),
        sa.CheckConstraint("length(trim(description)) > 0", name="ticket_description_nonempty"))
    for column in ("category", "priority", "status", "created_by", "assigned_to", "created_at"):
        op.create_index(f"ix_tickets_{column}", "tickets", [column])


def downgrade():
    op.drop_table("tickets")
    op.drop_table("users")
    for name in ("ticket_status", "ticket_priority", "ticket_category", "user_role"):
        sa.Enum(name=name).drop(op.get_bind(), checkfirst=True)
