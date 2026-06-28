import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.rate_limit import limiter
from app.routers import auth, leads, orders

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="BlitzXCreatives API",
    description="Backend API for auth, project orders, and contact leads.",
    version="1.0.0",
)

app.state.limiter = limiter

# ---------- CORS ----------
# credentials: "include" on the frontend requires an explicit origin (not "*")
# and allow_credentials=True.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": "Too many requests. Please try again shortly."},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Flatten pydantic errors into a single readable message for the frontend's
    # `data.detail` handling. Raw error objects (e.g. ctx.error as ValueError)
    # aren't JSON-serializable, so we only forward plain string fields.
    raw_errors = exc.errors()
    first_error = raw_errors[0]
    field = ".".join(str(loc) for loc in first_error["loc"] if loc != "body")
    message = first_error["msg"]

    safe_errors = [
        {"loc": list(e["loc"]), "msg": e["msg"], "type": e["type"]}
        for e in raw_errors
    ]

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": f"{field}: {message}" if field else message, "errors": safe_errors},
    )


app.include_router(auth.router)
app.include_router(orders.router)
app.include_router(leads.router)


@app.get("/")
async def root():
    return {"status": "ok", "service": "blitzx-backend"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
