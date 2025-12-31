from __future__ import annotations

import os
import logging
import sys
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.admin import router as admin_router
from app.api.public import router as public_router
from app.core.config import get_settings, Settings
from app.db import engine
from app.models import Base


def setup_logging(settings: Settings):
    """配置日志系统"""
    # 创建日志格式
    log_format = "[%(asctime)s] %(levelname)s in %(name)s: %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # 配置根日志记录器
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format=log_format,
        datefmt=date_format,
        handlers=[logging.StreamHandler(sys.stdout)]
    )

    # 设置 uvicorn 访问日志
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    # 设置 uvicorn 错误日志
    logging.getLogger("uvicorn.error").setLevel(logging.ERROR)

    return logging.getLogger(__name__)


def create_app() -> FastAPI:
    settings = get_settings()
    logger = setup_logging(settings)

    # 启动日志
    logger.info("=" * 50)
    logger.info("🍵 来喝茶 API Starting...")
    logger.info(f"Environment: {settings.app_env}")
    logger.info(f"Log Level: {settings.log_level}")
    logger.info(f"CORS Origins: {settings.cors_origins if settings.cors_origins else 'Not configured'}")
    logger.info("=" * 50)

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
    logger.info(f"Static files mounted at /uploads -> {uploads_dir}")

    app.include_router(public_router)
    app.include_router(admin_router)
    logger.info("Routers registered: /api (public), /api/admin (admin)")

    @app.get("/health")
    def health():
        return {"ok": True}

    @app.on_event("startup")
    def _startup():
        logger.info("Creating database tables if not exist...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database initialization completed")
        logger.info("🚀 Server is ready to accept requests")
        logger.info("=" * 50)

    return app


app = create_app()
