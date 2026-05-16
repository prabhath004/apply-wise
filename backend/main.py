from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import analysis, health, outreach, resumes, settings
from app.core.config import get_settings
from app.core.errors import AppError
from app.db.session import init_db


def create_app() -> FastAPI:
    app = FastAPI(title="ApplyIntel Local Backend", version="0.1.0")
    config = get_settings()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_origin_regex=config.cors_origin_regex,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(settings.router)
    app.include_router(resumes.router)
    app.include_router(analysis.router)
    app.include_router(outreach.router)

    @app.exception_handler(AppError)
    def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"error": exc.code, "message": exc.message})

    @app.on_event("startup")
    def on_startup() -> None:
        init_db()

    return app


app = create_app()
