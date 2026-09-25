from __future__ import annotations

import os
from collections.abc import Awaitable, Callable
from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field, StrictBool

from app.services.attestation import ConfidentialSpaceAttestationProvider
from app.services.demo_service import DemoService
from app.services.proposer import DeterministicFakeProposer, RealGeminiProposer

APP_ROOT = Path(__file__).resolve().parent
CONFIG_DIR = APP_ROOT / "config"
WEB_DIR = APP_ROOT / "web"


class RunRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str = Field(min_length=8, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")
    explicit_user_confirmation: StrictBool = False


def _build_service() -> DemoService:
    mode = os.getenv("APP_MODE", "offline_demo")
    config_dir = Path(os.getenv("APP_CONFIG_DIR", str(CONFIG_DIR))).resolve()
    if mode == "offline_demo":
        return DemoService(
            config_dir=config_dir,
            proposer=DeterministicFakeProposer(),
            offline=True,
        )
    if mode == "live":
        model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        attestation_mode = os.getenv("ATTESTATION_MODE", "local")
        attestation_provider = (
            ConfidentialSpaceAttestationProvider()
            if attestation_mode == "confidential_space"
            else None
        )
        return DemoService(
            config_dir=config_dir,
            proposer=RealGeminiProposer(model_identifier=model),
            offline=False,
            attestation_provider=attestation_provider,
        )
    raise ValueError("APP_MODE must be 'offline_demo' or 'live'")


def create_app(service: DemoService | None = None) -> FastAPI:
    app = FastAPI(
        title="Verifiable AI Boundary",
        version="0.1.0",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    demo_service = service or _build_service()
    app.state.demo_service = demo_service

    @app.middleware("http")
    async def security_headers(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "img-src 'self' data:; connect-src 'self'; object-src 'none'; "
            "base-uri 'none'; frame-ancestors 'none'"
        )
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

    @app.get("/healthz")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/state")
    def state() -> dict[str, object]:
        return demo_service.state()

    @app.post("/api/run")
    def run(request: RunRequest) -> dict[str, object]:
        return demo_service.run(
            request_id=request.request_id,
            explicit_user_confirmation=request.explicit_user_confirmation,
        ).model_dump(mode="json")

    @app.post("/api/poison")
    def poison() -> dict[str, object]:
        return demo_service.poison()

    @app.post("/api/reset")
    def reset() -> dict[str, object]:
        return demo_service.reset()

    @app.get("/", include_in_schema=False)
    def index() -> FileResponse:
        return FileResponse(WEB_DIR / "index.html")

    app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")
    return app


app = create_app()
