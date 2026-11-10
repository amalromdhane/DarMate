import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy.exc import IntegrityError
from pathlib import Path
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.exceptions import AppError
from app.core.rate_limit import limiter
from app.presentation.api.v1.router import api_router

logger = logging.getLogger("darmate")

app = FastAPI(title=settings.app_name, version="1.0.0",
              docs_url=None if settings.is_production else "/docs",
              redoc_url=None if settings.is_production else "/redoc")
app.state.limiter = limiter

app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"], allow_headers=["Authorization", "Content-Type"])


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "same-origin")
    if settings.is_production:
        response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
    return response


@app.exception_handler(AppError)
async def app_error_handler(_: Request, exc: AppError):
    return JSONResponse({"detail": exc.message}, status_code=exc.status_code)


@app.exception_handler(IntegrityError)
async def integrity_handler(_: Request, exc: IntegrityError):
    logger.warning("Integrity error: %s", exc.orig)
    return JSONResponse({"detail": "Opération impossible : cet élément existe déjà ou est utilisé ailleurs."}, status_code=409)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(_: Request, exc: RateLimitExceeded):
    return JSONResponse({"detail": "Trop de requêtes. Patientez un instant avant de réessayer."}, status_code=429)


@app.exception_handler(RequestValidationError)
async def validation_handler(_: Request, exc: RequestValidationError):
    fields = [{"field": ".".join(str(p) for p in e["loc"][1:]), "message": e["msg"]} for e in exc.errors()]
    return JSONResponse({"detail": "Certaines données sont invalides.", "errors": fields}, status_code=422)


@app.exception_handler(Exception)
async def unhandled_handler(_: Request, exc: Exception):
    logger.exception("Erreur non gérée")  # détails uniquement dans les logs
    return JSONResponse({"detail": "Une erreur interne est survenue. Réessayez plus tard."}, status_code=500)


# Seules les photos d'annonces (public/) sont servies statiquement ; private/ ne l'est jamais.
_public = Path(settings.upload_dir).resolve() / "public"
_public.mkdir(parents=True, exist_ok=True)
app.mount("/media/public", StaticFiles(directory=_public), name="media")

app.include_router(api_router, prefix="/api/v1")
