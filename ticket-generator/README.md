# Deskflow — IT Helpdesk

A working conventional ticketing MVP: React + TypeScript + Vite + Tailwind CSS, FastAPI + SQLAlchemy 2 + Pydantic, PostgreSQL 16, and Alembic. No AI functionality is included.

## Start with Docker

Install Docker Desktop with Linux containers enabled and Docker Compose v2. From this directory:

```powershell
docker compose up --build
```

Defaults work without a `.env` file. To customize settings, first run `Copy-Item .env.example .env` (Windows) or `cp .env.example .env` (macOS/Linux).

- Frontend: http://localhost:5173
- Backend health: http://localhost:8001/api/health
- Swagger UI: http://localhost:8001/docs
- OpenAPI JSON: http://localhost:8001/openapi.json

Compose waits for PostgreSQL, applies migrations, seeds accounts and ten tickets, starts the API, and then starts the frontend. Database data persists in the `postgres_data` Docker volume. `docker compose down` stops containers without removing data. Run in the background with `docker compose up --build -d`; inspect logs with `docker compose logs -f backend`.

The browser uses `VITE_API_BASE_URL=http://localhost:8001`, not the internal `backend` hostname. This setting is baked into the frontend build; rebuild after changing it. If you change ports, also update `VITE_API_BASE_URL` and `CORS_ORIGINS`. The internal API port remains 8001. If database credentials change, update `DATABASE_URL` too (URL-encode special characters). PostgreSQL is not exposed on the host; access it with `docker compose exec db psql -U helpdesk -d helpdesk`.

## Development-only identity

**This application has no secure authentication.** `X-Demo-User-Id` permits anyone to impersonate any account. Backend checks enforce role and ownership rules for the selected mock identity, but those checks do not establish a user's real identity. Use only in a trusted local development environment. Compose binds exposed ports to localhost. `DEMO_AUTH_ENABLED=false` disables the mock account directory and protected ticket endpoints; a real authentication system must be integrated before deployment.

Seeded accounts on a fresh database:

| ID | Name | Role |
|---|---|---|
| 1 | Alex Morgan | Employee |
| 2 | Priya Sharma | Employee |
| 3 | Jamie Chen | Employee |
| 4 | Sam Rivera | Support agent |
| 5 | Jordan Lee | Support agent |

Use the frontend selector to switch accounts. IDs are database-generated; `/api/users` is the authoritative directory. Employees create tickets for themselves, read only their own tickets and statistics, and cannot patch tickets. Agents read all tickets and update status, priority, and assignment. Agents do not submit employee requests. Inaccessible employee tickets return 404. Assignment must reference a support agent, or null to unassign.

## REST API

| Method | Path | Behavior |
|---|---|---|
| GET | `/api/health` | Live database readiness check, no identity required |
| GET | `/api/users` | Mock account directory, no identity required |
| POST | `/api/tickets` | Employee creates ticket; 201, generated ID and Location header |
| GET | `/api/tickets` | Scoped search and pagination |
| GET | `/api/tickets/stats` | Scoped dashboard totals, including closed |
| GET | `/api/tickets/{id}` | Complete ticket including creator and assignee |
| PATCH | `/api/tickets/{id}` | Agent updates status, priority, or assigned_to |

All ticket requests require `X-Demo-User-Id`. In Swagger, fill in this header on each ticket operation. Category: `HARDWARE`, `SOFTWARE`, `NETWORK`, `ACCESS`, `OTHER`. Priority: `LOW`, `MEDIUM` (default), `HIGH`, `CRITICAL`. Status: `OPEN` (default), `IN_PROGRESS`, `RESOLVED`, `CLOSED`.

Using curl (on Windows use `curl.exe`; shell quoting differs, so PowerShell examples follow):

```bash
curl -X POST http://localhost:8001/api/tickets \
  -H 'Content-Type: application/json' -H 'X-Demo-User-Id: 1' \
  -d '{"title":"Laptop screen damaged","description":"The display is cracked.","category":"HARDWARE","priority":"MEDIUM","created_by":1}'

curl 'http://localhost:8001/api/tickets?search=laptop&status=OPEN&page=1&page_size=10' \
  -H 'X-Demo-User-Id: 1'

curl -X PATCH http://localhost:8001/api/tickets/1 \
  -H 'Content-Type: application/json' -H 'X-Demo-User-Id: 4' \
  -d '{"status":"IN_PROGRESS","priority":"HIGH","assigned_to":4}'
```

PowerShell:

```powershell
$employeeHeaders = @{ 'X-Demo-User-Id' = '1' }
$ticketBody = @{ title='Laptop screen damaged'; description='The display is cracked.'; category='HARDWARE'; created_by=1 } | ConvertTo-Json
$ticket = Invoke-RestMethod http://localhost:8001/api/tickets -Method Post -Headers $employeeHeaders -ContentType 'application/json' -Body $ticketBody
Invoke-RestMethod "http://localhost:8001/api/tickets/$($ticket.id)" -Headers $employeeHeaders
$agentHeaders = @{ 'X-Demo-User-Id' = '4' }
Invoke-RestMethod "http://localhost:8001/api/tickets/$($ticket.id)" -Method Patch -Headers $agentHeaders -ContentType 'application/json' -Body '{"status":"IN_PROGRESS","assigned_to":4}'
```

List filters: `status`, `category`, `priority`, `created_by`, `assigned_to`, `search`, `page` (1+), `page_size` (1–100, default 10). Filters combine; employee ownership always applies. Search matches literal substrings in title and description, case-insensitively, including escaped `%` and `_`. Results are ordered newest first with ID as a tie breaker:

```json
{"items": [], "total": 0, "page": 1, "page_size": 10, "total_pages": 0}
```

Errors consistently return `{"error":{"code":"validation_error","message":"Request validation failed","details":[{"location":["body","title"],"message":"...","type":"..."}]}}`. Business-rule errors use the same envelope with an empty details list. Unknown/empty fields and invalid enums are rejected with 422. Missing/unknown identity returns 401, forbidden actions 403, missing/inaccessible tickets 404, and unavailable services 503. Timestamps are UTC ISO 8601 strings and update automatically when the ticket is managed. Partial PATCH supports only the three management fields and rejects empty patches or null status/priority.

## Tests and build checks

```powershell
docker compose run --rm backend pytest -q
docker compose run --rm frontend npm run build
docker compose exec backend python scripts/smoke_test.py
```

Backend tests use an isolated in-memory SQLite database with foreign keys enabled; they never modify your PostgreSQL tickets. They cover creation, validation, retrieval, filters, pagination, literal search, status/priority/assignment changes, role/ownership restrictions, statistics, identity, and disabled mock auth. Production storage uses PostgreSQL; run the migration checks below against PostgreSQL as well.

The live smoke script checks the running API against PostgreSQL, verifies that seeding twice leaves record counts unchanged, and deletes only its own temporary verification ticket afterward. It requires the backend service to be running.

## Local development without app containers

Requires Python 3.12+, Node.js 22+, and a PostgreSQL 16+ instance. You can start just the database with `docker compose up -d db` and add a host mapping `127.0.0.1:5432:5432` to the db service for local backend access.

Backend (PowerShell, from repository root):

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:DATABASE_URL='postgresql+psycopg://helpdesk:helpdesk@localhost:5432/helpdesk'
$env:CORS_ORIGINS='http://localhost:5173'
alembic upgrade head
python -m app.services.seed
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

Frontend, in another terminal:

```powershell
cd frontend
npm ci
$env:VITE_API_BASE_URL='http://localhost:8001'
npm run dev
```

On macOS/Linux use `python3 -m venv .venv`, `source .venv/bin/activate`, and `export NAME=value`. Run `pytest -q` from `backend` or `npm run build` from `frontend`.

## Migrations and seed data

```powershell
docker compose exec backend alembic current
docker compose exec backend alembic check
docker compose exec backend python -m app.services.seed
```

The initial migration explicitly creates enums, users, tickets, foreign keys, search/filter indexes, title/description constraints, and unique user emails. The seed uses user email and ticket title/creator keys to avoid duplicates on restart. It does not reset existing ticket changes. To add a migration: `docker compose exec backend alembic revision --autogenerate -m "describe change"`, review the generated file, then apply `alembic upgrade head`. The image filesystem is not a source bind mount; copy generated migrations back to the source directory before rebuilding, or generate them in local development.

## Manual acceptance checks

1. Start Compose and confirm `/api/health` and Swagger respond.
2. Select Alex: dashboard and My Tickets show only Alex's tickets. Search, combine filters, and change page size.
3. Create a ticket with title, description, category, and priority; verify redirect to details and success notification.
4. Select Priya: Alex's ticket should not be accessible, even by a direct detail URL.
5. Select Sam: All Tickets includes the new request. Update status/priority, assign to Jordan, save, and then unassign.
6. Switch back to Alex: management is read-only and saved information is visible.
7. Restart Compose: tickets and management changes persist; sample users/tickets are not duplicated.
8. Verify mobile navigation, empty search, API error/retry state, and keyboard form navigation.

## Structure

`backend/app/api` contains routes and development identity dependencies; `models`, `schemas`, `database`, `core`, and `services` contain persistence, validation, configuration, and seeding. `backend/alembic` holds migrations. `frontend/src/pages` contains Dashboard, Tickets, Create Ticket, and Ticket Details; `components` holds shared UI/context, `services` the REST client, and `types` the API contracts.
