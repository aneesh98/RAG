# Project Requirements: IT Helpdesk Ticketing System

## 1. Project Overview

Develop a full-stack IT Helpdesk Ticketing System that allows employees to create and track IT support tickets and enables IT support personnel to manage and resolve them.

The application must include a React frontend, a FastAPI backend, and a PostgreSQL database.

The system must expose REST APIs for all ticket operations so that external applications can interact with it programmatically.

**Important:** This project is strictly a conventional ticket management application. Do not implement any AI, LLM, RAG, chatbot, agent, tool-calling, or MCP functionality. These capabilities will be developed separately and integrated later through the REST APIs.

## 2. Technology Stack

- **Frontend:** React with TypeScript, Vite, and Tailwind CSS.
- **Backend:** Python 3.12+ with FastAPI.
- **Database:** PostgreSQL 16 or later.
- **ORM:** SQLAlchemy 2.x.
- **Validation:** Pydantic.
- **Database migrations:** Alembic.
- **Containerization:** Docker and Docker Compose.
- **API documentation:** FastAPI-generated OpenAPI/Swagger documentation.

Use a clean, modular architecture with separate frontend, backend, and database components.

## 3. User Roles

The system must support two types of users.

### Employee

Employees can:

- Create new IT support tickets.
- View their submitted tickets.
- View ticket details and current status.
- Search and filter their tickets.

### IT Support Agent

IT support agents can:

- View all submitted tickets.
- Search and filter tickets.
- View ticket details.
- Update ticket status.
- Assign tickets to support agents.

For the MVP, implement a simple mock-user mechanism with predefined employee and support-agent accounts. Provide a user selector in the frontend to switch between them.

Real authentication is not required. Clearly mark mock authentication as development-only, and do not present it as a secure access-control mechanism.

## 4. Ticket Data Model

Each ticket must contain the following fields:

| Field | Type | Description |
|---|---|---|
| id | Integer | Auto-generated primary key |
| title | String | Short summary of the issue |
| description | Text | Detailed issue description |
| category | Enum | Type of IT issue |
| priority | Enum | Priority of the issue |
| status | Enum | Current ticket status |
| created_by | Integer | ID of the employee who created the ticket |
| assigned_to | Integer, nullable | ID of the assigned support agent |
| created_at | Timestamp | Ticket creation time |
| updated_at | Timestamp | Last modification time |

### Supported Categories

- HARDWARE
- SOFTWARE
- NETWORK
- ACCESS
- OTHER

### Supported Priorities

- LOW
- MEDIUM
- HIGH
- CRITICAL

Default priority: MEDIUM.

### Supported Statuses

- OPEN
- IN_PROGRESS
- RESOLVED
- CLOSED

Default status: OPEN.

The database must also contain a `users` table with user ID, name, email, and role.

Use foreign keys for `created_by` and `assigned_to`.

## 5. Backend Requirements

Develop a FastAPI REST API with the following endpoints.

### Ticket Operations

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/tickets` | Create a ticket |
| GET | `/api/tickets` | Retrieve tickets with filtering and pagination |
| GET | `/api/tickets/{ticket_id}` | Retrieve a ticket by ID |
| PATCH | `/api/tickets/{ticket_id}` | Update ticket status, priority, or assignment |
| GET | `/api/users` | Retrieve available users |
| GET | `/api/health` | Application health check |

### Ticket Creation Example

Request:

```json
{
  "title": "Laptop screen damaged",
  "description": "My company laptop screen cracked after an accidental fall.",
  "category": "HARDWARE",
  "priority": "MEDIUM",
  "created_by": 1
}
```

Response:

```json
{
  "id": 1042,
  "title": "Laptop screen damaged",
  "description": "My company laptop screen cracked after an accidental fall.",
  "category": "HARDWARE",
  "priority": "MEDIUM",
  "status": "OPEN",
  "created_by": 1,
  "assigned_to": null,
  "created_at": "2026-10-10T10:30:00Z",
  "updated_at": "2026-10-10T10:30:00Z"
}
```

### Filtering

`GET /api/tickets` must support optional query parameters:

- `status`
- `category`
- `priority`
- `created_by`
- `assigned_to`
- `search`
- `page`
- `page_size`

Search should support case-insensitive matching against ticket titles and descriptions.

Responses for ticket collections must include pagination metadata.

### Validation and Error Handling

- Reject missing or empty required fields.
- Reject invalid category, priority, or status values.
- Return HTTP 404 when a ticket does not exist.
- Return HTTP 422 for invalid request data.
- Use consistent JSON error responses.
- Automatically maintain timestamps.
- Prevent employees from modifying fields reserved for support agents.
- Enforce authorization rules in the backend, not only the frontend.

For the local MVP, mock identity can be passed through a development-only header such as `X-Demo-User-Id`. Resolve the corresponding user and role on the backend. Document that this is not secure authentication.

## 6. Frontend Requirements

Build a modern, responsive web interface suitable for an internal enterprise IT helpdesk.

The frontend must communicate with the FastAPI backend using REST APIs. Do not use hardcoded ticket data except for clearly identified mock-user configuration.

### 6.1 Dashboard

The dashboard should display:

- Total tickets.
- Open tickets.
- In-progress tickets.
- Resolved tickets.
- Recently created tickets.

Employees should see statistics for their own tickets. IT agents should see system-wide statistics.

### 6.2 Ticket List Page

Display tickets in a table with:

- Ticket ID.
- Title.
- Category.
- Priority.
- Status.
- Created by.
- Assigned agent.
- Creation date.

Provide:

- Search input.
- Status filter.
- Category filter.
- Priority filter.
- Pagination.
- Clickable ticket rows.

Use visually distinct status and priority indicators.

### 6.3 Create Ticket Page

Provide a form containing:

- Title.
- Description.
- Category dropdown.
- Priority dropdown.
- Submit button.

Include client-side validation and display backend validation errors when applicable.

After successful submission, redirect to the newly created ticket's detail page and display a success notification.

### 6.4 Ticket Detail Page

Display:

- Ticket ID and title.
- Full description.
- Category.
- Priority.
- Status.
- Employee information.
- Assigned agent.
- Creation and modification timestamps.

For IT support agents, provide controls to:

- Change ticket status.
- Change ticket priority.
- Assign or reassign a support agent.

Employees should have read-only access to these management controls.

### 6.5 Navigation and User Experience

Provide:

- Sidebar or top navigation.
- Dashboard link.
- My Tickets / All Tickets link.
- Create Ticket button.
- Mock-user selector.
- Loading indicators.
- Empty states.
- Success and error notifications.
- Responsive layouts for desktop and mobile screens.

The interface should have a clean, professional appearance similar to an internal enterprise support portal.

## 7. Database Requirements

Use PostgreSQL with SQLAlchemy ORM models and Alembic migrations.

Create the necessary tables, relationships, indexes, and constraints.

Include seed data containing:

- At least three employees.
- At least two IT support agents.
- Approximately ten sample tickets distributed across categories, priorities, and statuses.

Seed operations must be idempotent so restarting the application does not create duplicate records.

## 8. Docker and Local Development

Provide a `docker-compose.yml` that starts:

1. PostgreSQL.
2. FastAPI backend.
3. React frontend.

The complete application must be startable with:

```bash
docker compose up --build
```

Suggested local endpoints:

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8001`
- Swagger UI: `http://localhost:8001/docs`
- PostgreSQL: internal container port `5432`, with optional host port mapping configurable through environment variables.

Use environment variables for database credentials, connection strings, and API base URLs.

Provide a `.env.example` file.

PostgreSQL must use a persistent Docker volume.

The frontend and backend must be configured to communicate correctly when running inside Docker Compose.

## 9. Code Organization

Use a structure similar to:

```text
it-helpdesk/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── types/
│   │   └── App.tsx
│   ├── Dockerfile
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── database/
│   │   └── core/
│   ├── alembic/
│   ├── Dockerfile
│   └── requirements.txt
│
├── docker-compose.yml
├── .env.example
└── README.md
```

The exact directory structure may be adjusted if a cleaner design is appropriate.

## 10. Testing Requirements

Include basic backend automated tests covering:

- Successful ticket creation.
- Invalid ticket creation requests.
- Ticket retrieval.
- Ticket not found.
- Ticket filtering.
- Ticket status updates.
- Role-based operation restrictions.

Use pytest.

Frontend tests are optional for the MVP, but the interface must be manually verifiable.

## 11. API Integration Requirements

The REST API must be designed for consumption by external applications, not only the React frontend.

Ensure that:

- All ticket operations are available through documented JSON APIs.
- API requests and responses use consistent structures.
- Endpoints do not depend on browser-specific behavior.
- Ticket creation returns the generated ticket ID.
- Ticket retrieval returns complete structured ticket information.
- Validation errors are machine-readable.
- OpenAPI documentation accurately describes available endpoints and request schemas.
- CORS is configured for the local frontend development origin.

The backend must not contain any AI-specific code.

## 12. Out of Scope

Do not implement:

- LLM integrations.
- AI chat interfaces.
- RAG pipelines.
- Embeddings or vector databases.
- LLM tool calling.
- AI agents.
- MCP servers.
- External ticketing platforms such as Jira or ServiceNow.
- Email notifications.
- File attachments.
- Complex SLA management.
- Enterprise SSO or production authentication.

These features may be added in future iterations.

## 13. Acceptance Criteria

The application will be considered complete when:

1. The entire system starts successfully using Docker Compose.
2. Users can access the React frontend.
3. Employees can create tickets using the frontend.
4. Created tickets are persisted in PostgreSQL.
5. Employees can view and search their tickets.
6. IT support agents can view all tickets.
7. IT support agents can update ticket status, priority, and assignment.
8. Ticket information is consistent between the frontend and REST API.
9. REST endpoints can be independently tested using Swagger UI or curl.
10. Database migrations and seed data work correctly.
11. Backend validation and role restrictions are enforced.
12. The README explains installation, startup, API usage, and testing.

## 14. Instructions to the Code-Generation Agent

Generate the complete working application according to the requirements above.

Do not generate only scaffolding, pseudocode, or illustrative snippets. Implement the actual frontend pages, backend routes, database models, migrations, API integration, Docker configuration, seed data, and tests.

Prioritize a functional, straightforward MVP over unnecessary architectural complexity.

Ensure that the frontend is connected to real backend endpoints and that ticket operations persist in PostgreSQL.

Provide a README with exact commands for starting, testing, and accessing the application.

**Do not implement any AI functionality. The ticketing system will be integrated with a separately developed AI assistant in a later phase.**