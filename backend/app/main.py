from __future__ import annotations

import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.admin import router as admin_router
from app.api.public import router as public_router
from app.core.config import get_settings
from app.db import engine
from app.models import Base


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(title="来喝茶 API", version="0.1.0")

    if settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=True,
            allow_methods=["*"] ,
            allow_headers=["*"],
        )

    # 静态上传文件
    uploads_dir = os.path.join(os.path.dirname(__file__), "..", "data", "uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

    app.include_router(public_router)
    app.include_router(admin_router)

    @app.get("/health")
    def health():
        return {"ok": True}

    @app.on_event("startup")
    def _startup():
        Base.metadata.create_all(bind=engine)

    return app


app = create_app()
