from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from app.database.session import SessionLocal
from app.models import User, Ticket, Role, Category, Priority, Status

ACCOUNTS = [
    ("Alex Morgan", "alex.morgan@example.com", Role.EMPLOYEE),
    ("Priya Sharma", "priya.sharma@example.com", Role.EMPLOYEE),
    ("Jamie Chen", "jamie.chen@example.com", Role.EMPLOYEE),
    ("Sam Rivera", "sam.rivera@example.com", Role.SUPPORT_AGENT),
    ("Jordan Lee", "jordan.lee@example.com", Role.SUPPORT_AGENT),
]
SAMPLES = [
    ("Laptop display flickers", "The display flickers when my laptop is connected to the docking station.", Category.HARDWARE, Priority.HIGH, Status.OPEN),
    ("VPN connection drops", "The remote access VPN disconnects every few minutes on my home network.", Category.NETWORK, Priority.HIGH, Status.IN_PROGRESS),
    ("Access to shared finance folder", "Please grant read access to the finance team's shared project folder.", Category.ACCESS, Priority.MEDIUM, Status.OPEN),
    ("Design software won't launch", "The design application stops at the loading screen after yesterday's update.", Category.SOFTWARE, Priority.HIGH, Status.IN_PROGRESS),
    ("Meeting room keyboard replacement", "The wireless keyboard in meeting room 3 has several broken keys.", Category.HARDWARE, Priority.LOW, Status.RESOLVED),
    ("Office Wi-Fi unavailable", "The third-floor wireless network is unavailable for the whole team.", Category.NETWORK, Priority.CRITICAL, Status.OPEN),
    ("Password reset request", "I am locked out of the internal expense portal and need a password reset.", Category.ACCESS, Priority.MEDIUM, Status.RESOLVED),
    ("Spreadsheet application update", "Please update my spreadsheet application to the approved version.", Category.SOFTWARE, Priority.LOW, Status.CLOSED),
    ("New desk setup assistance", "I need help connecting monitors and peripherals at my new workstation.", Category.OTHER, Priority.MEDIUM, Status.OPEN),
    ("Printer produces blank pages", "The shared printer produces blank pages even after replacing the toner.", Category.HARDWARE, Priority.MEDIUM, Status.CLOSED),
]


def seed():
    # Stable natural keys: restarting never duplicates users or sample tickets.
    with SessionLocal.begin() as db:
        accounts = []
        for name, email, role in ACCOUNTS:
            user = db.scalar(select(User).where(User.email == email))
            if user is None:
                user = User(name=name, email=email, role=role)
                db.add(user)
                db.flush()
            accounts.append(user)
        for i, (title, description, category, priority, status) in enumerate(SAMPLES):
            creator = accounts[i % 3]
            existing = db.scalar(select(Ticket.id).where(Ticket.title == title, Ticket.created_by == creator.id))
            if existing is None:
                created = datetime.now(timezone.utc) - timedelta(days=9 - i, hours=2)
                db.add(Ticket(title=title, description=description, category=category, priority=priority, status=status, created_by=creator.id, assigned_to=accounts[3 + i % 2].id if status != Status.OPEN else None, created_at=created, updated_at=created))


if __name__ == "__main__":
    seed()
