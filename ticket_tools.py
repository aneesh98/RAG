import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


BASE_URL = "http://localhost:8001"

# Application configuration, not an argument supplied by the model.
DEMO_USER_ID = 1


def get_ticket(ticket_id: int) -> dict:
    # Model-generated arguments must be treated as untrusted input.
    if type(ticket_id) is not int or ticket_id <= 0:
        return {
            "ok": False,
            "error": "invalid_ticket_id",
            "message": "ticket_id must be a positive integer.",
        }

    request = Request(
        url=f"{BASE_URL}/api/tickets/{ticket_id}",
        headers={
            "Accept": "application/json",
            "X-Demo-User-Id": str(DEMO_USER_ID),
        },
        method="GET",
    )

    try:
        with urlopen(request, timeout=10) as response:
            ticket = json.load(response)

        return {
            "ok": True,
            "ticket": ticket,
        }

    except HTTPError as exc:
        messages = {
            401: "The API rejected the configured demo identity.",
            403: "The configured user cannot perform this operation.",
            404: "The ticket was not found or is not visible to this user.",
            422: "The API rejected the request parameters.",
            503: "The ticket service is unavailable.",
        }

        return {
            "ok": False,
            "error": "ticket_api_error",
            "status_code": exc.code,
            "message": messages.get(
                exc.code,
                "The ticket API returned an error.",
            ),
        }

    except (URLError, TimeoutError):
        return {
            "ok": False,
            "error": "connection_failed",
            "message": "Could not reach the ticket API within the timeout.",
        }

    except (ValueError, UnicodeError):
        return {
            "ok": False,
            "error": "invalid_response",
            "message": "The ticket API did not return valid JSON.",
        }


def create_ticket(
    title: str,
    description: str,
    category: str,
    priority: str = "MEDIUM",
    *,
    confirm=None
) -> dict:
    # Validate types before calling string methods.
    values = (title, description, category, priority)

    if not all(isinstance(value, str) for value in values):
        return {
            "ok": False,
            "error": "invalid_arguments",
            "message": "All ticket fields must be strings.",
        }

    title = title.strip()
    description = description.strip()
    category = category.strip().upper()
    priority = priority.strip().upper()

    if not 1 <= len(title) <= 200:
        return {
            "ok": False,
            "error": "invalid_title",
            "message": "Title must contain 1–200 characters.",
        }

    if not 1 <= len(description) <= 20000:
        return {
            "ok": False,
            "error": "invalid_description",
            "message": "Description must contain 1–20000 characters.",
        }

    if category not in {
        "HARDWARE", "SOFTWARE", "NETWORK", "ACCESS", "OTHER"
    }:
        return {
            "ok": False,
            "error": "invalid_category",
            "message": "Choose HARDWARE, SOFTWARE, NETWORK, ACCESS, or OTHER.",
        }

    if priority not in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}:
        return {
            "ok": False,
            "error": "invalid_priority",
            "message": "Choose LOW, MEDIUM, HIGH, or CRITICAL.",
        }

    payload = {
        "title": title,
        "description": description,
        "category": category,
        "priority": priority,
        "created_by": DEMO_USER_ID,
    }

    # Confirmation is collected directly from the human.
    print("\nTicket to create:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))

    if confirm is None:
        # Preserve the original terminal workflow.
        print("\nTicket to create:")
        print(json.dumps(payload, indent=2, ensure_ascii=False))

        try:
            approved = input("\nType CREATE to submit this ticket: ") == "CREATE"
        except (EOFError, KeyboardInterrupt):
            approved = False
    else:
        approved = confirm(payload) is True

    if not approved:
        return {
            "ok": False,
            "error": "cancelled",
            "message": "Ticket creation cancelled. No request was sent.",
        }

    request = Request(
        url=f"{BASE_URL}/api/tickets",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Demo-User-Id": str(DEMO_USER_ID),
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=10) as response:
            ticket = json.load(response)

        return {
            "ok": True,
            "ticket": ticket,
        }

    except HTTPError as exc:
        messages = {
            401: "The API rejected the configured demo identity.",
            403: "Only employees can create tickets for themselves.",
            422: "The API rejected the ticket fields.",
            503: "The ticket service is unavailable.",
        }

        return {
            "ok": False,
            "error": "ticket_api_error",
            "status_code": exc.code,
            "message": messages.get(
                exc.code,
                "The API returned an error. Verify whether the ticket "
                "exists before submitting again.",
            ),
        }

    except (URLError, TimeoutError, ValueError, UnicodeError):
        return {
            "ok": False,
            "error": "creation_unconfirmed",
            "message": (
                "Could not confirm ticket creation. The request may "
                "have reached the server. Check your tickets before "
                "submitting again."
            ),
        }

CREATE_TICKET_TOOL = {
    "type": "function",
    "name": "create_ticket",
    "description": (
        "Create an IT support ticket when the user explicitly requests "
        "ticket creation. Collect missing details before requesting this "
        "tool. The application requires human confirmation before submission."
    ),
    "strict": True,
    "parameters": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "A short summary of the reported IT problem.",
                "minLength": 1,
                "maxLength": 200,
            },
            "description": {
                "type": "string",
                "description": (
                    "Details provided by the user about the problem. "
                    "Do not invent symptoms or circumstances."
                ),
                "minLength": 1,
                "maxLength": 20000,
            },
            "category": {
                "type": "string",
                "enum": [
                    "HARDWARE",
                    "SOFTWARE",
                    "NETWORK",
                    "ACCESS",
                    "OTHER",
                ],
                "description": "The category that best matches the IT problem.",
            },
            "priority": {
                "type": "string",
                "enum": ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
                "description": (
                    "Use MEDIUM unless the user provides information "
                    "supporting another priority."
                ),
            },
        },
        "required": [
            "title",
            "description",
            "category",
            "priority",
        ],
        "additionalProperties": False,
    },
}