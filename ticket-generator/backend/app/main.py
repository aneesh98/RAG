import logging
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException
from app.api.routes import router
from app.core.config import settings

app = FastAPI(title="IT Helpdesk API", version="1.0.0", description="Conventional IT ticket management REST API. X-Demo-User-Id is DEVELOPMENT ONLY, allows impersonation, and is not secure authentication. Do not expose this MVP publicly.")
app.add_middleware(CORSMiddleware, allow_origins=[origin.strip() for origin in settings.cors_origins.split(",")], allow_credentials=False, allow_methods=["GET", "POST", "PATCH"], allow_headers=["Content-Type", "X-Demo-User-Id"])


@app.exception_handler(HTTPException)
async def http_error(request: Request, exc: HTTPException):
    codes = {401: "unauthorized", 403: "forbidden", 404: "not_found", 422: "validation_error", 503: "unavailable"}
    return JSONResponse(status_code=exc.status_code, content={"error": {"code": codes.get(exc.status_code, "request_error"), "message": str(exc.detail), "details": []}})


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    details = [{"location": list(e["loc"]), "message": e["msg"], "type": e["type"]} for e in exc.errors()]
    return JSONResponse(status_code=422, content={"error": {"code": "validation_error", "message": "Request validation failed", "details": details}})


@app.exception_handler(Exception)
async def internal_error(request: Request, exc: Exception):
    logging.getLogger(__name__).exception("Unhandled API error")
    return JSONResponse(status_code=500, content={"error": {"code": "internal_error", "message": "An unexpected error occurred", "details": []}})


app.include_router(router)
