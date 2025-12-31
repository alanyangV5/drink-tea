from __future__ import annotations

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import decode_token
from app.db import get_db


def require_admin(request: Request, db: Session = Depends(get_db)):
    settings = get_settings()
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail={"code": "unauthorized", "message": "missing token"})

    token = auth.removeprefix("Bearer ").strip()
    try:
        payload = decode_token(token, settings.jwt_secret)
    except Exception:
        raise HTTPException(status_code=401, detail={"code": "unauthorized", "message": "invalid token"})

    sub = payload.get("sub")
    if sub != settings.admin_username:
        raise HTTPException(status_code=401, detail={"code": "unauthorized", "message": "invalid subject"})

    return True
