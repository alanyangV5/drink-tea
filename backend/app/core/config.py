from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional
import os


def _split_csv(value: str) -> List[str]:
    return [x.strip() for x in value.split(",") if x.strip()]


@dataclass(frozen=True)
class Settings:
    app_env: str
    cors_origins: List[str]

    admin_username: str
    admin_password: Optional[str]
    admin_password_hash: Optional[str]

    jwt_secret: str
    jwt_expire_minutes: int


def get_settings() -> Settings:
    app_env = os.getenv("APP_ENV", "dev")
    cors_origins = _split_csv(os.getenv("APP_CORS_ORIGINS", ""))

    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin_password_hash = os.getenv("ADMIN_PASSWORD_HASH")

    jwt_secret = os.getenv("JWT_SECRET", "change-me-in-prod")
    jwt_expire_minutes = int(os.getenv("JWT_EXPIRE_MINUTES", "720"))

    return Settings(
        app_env=app_env,
        cors_origins=cors_origins,
        admin_username=admin_username,
        admin_password=admin_password,
        admin_password_hash=admin_password_hash,
        jwt_secret=jwt_secret,
        jwt_expire_minutes=jwt_expire_minutes,
    )
