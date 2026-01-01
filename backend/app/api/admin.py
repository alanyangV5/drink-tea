from __future__ import annotations

import os
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from passlib.exc import UnknownHashError
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.core.config import get_settings
from app.core.security import create_access_token, verify_password
from app.db import get_db
from app.models import Event, Feedback, Tea
from app.schemas import (
    DashboardRankOut,
    DashboardRankRow,
    DashboardSummaryOut,
    ImportCommitIn,
    ImportPreviewOut,
    ImportPreviewRow,
    LoginIn,
    TeaBase,
    TeaListOut,
    TeaOut,
    TokenOut,
)

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/login", response_model=TokenOut)
def login(body: LoginIn):
    settings = get_settings()
    if body.username != settings.admin_username:
        raise HTTPException(status_code=401, detail={"code": "unauthorized", "message": "bad credentials"})

    if settings.admin_password_hash:
        try:
            ok = verify_password(body.password, settings.admin_password_hash)
        except UnknownHashError:
            # 哈希格式无效，可能是配置错误
            raise HTTPException(
                status_code=500,
                detail={
                    "code": "config_error",
                    "message": "Invalid ADMIN_PASSWORD_HASH format. Use ADMIN_PASSWORD for plain text, or generate a valid bcrypt hash using scripts/gen-hash.py"
                }
            )
    elif settings.admin_password:
        ok = body.password == settings.admin_password
    else:
        # 默认拒绝：必须配置密码
        ok = False

    if not ok:
        raise HTTPException(status_code=401, detail={"code": "unauthorized", "message": "bad credentials"})

    token = create_access_token(settings.admin_username, settings.jwt_secret, settings.jwt_expire_minutes)
    return TokenOut(token=token)


@router.get("/teas", response_model=TeaListOut, dependencies=[Depends(require_admin)])
def admin_list_teas(
    keyword: Optional[str] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
):
    q = select(Tea)
    if keyword:
        q = q.where(Tea.name.like(f"%{keyword}%"))
    if status:
        q = q.where(Tea.status == status)
    if category:
        q = q.where(Tea.category == category)

    q = q.order_by(Tea.updated_at.desc(), Tea.id.desc())

    total = db.execute(select(func.count()).select_from(q.subquery())).scalar_one()
    rows = db.execute(q.offset((page - 1) * page_size).limit(page_size)).scalars().all()

    items = [
        TeaOut(
            id=r.id,
            name=r.name,
            category=r.category,
            year=r.year,
            origin=r.origin,
            spec=r.spec,
            price_min=r.price_min,
            price_max=r.price_max,
            intro=r.intro,
            cover_url=r.cover_url,
            status=r.status,
            weight=r.weight,
            created_at=r.created_at,
            updated_at=r.updated_at,
        )
        for r in rows
    ]
    return TeaListOut(items=items, page=page, page_size=page_size, total=total)


@router.post("/teas", response_model=TeaOut, dependencies=[Depends(require_admin)])
def admin_create_tea(body: TeaBase, db: Session = Depends(get_db)):
    now = datetime.utcnow()
    tea = Tea(
        name=body.name,
        category=body.category,
        year=body.year,
        origin=body.origin,
        spec=body.spec,
        price_min=body.price_min,
        price_max=body.price_max,
        intro=body.intro,
        cover_url=body.cover_url,
        status=body.status,
        weight=body.weight,
        created_at=now,
        updated_at=now,
    )
    db.add(tea)
    db.commit()
    db.refresh(tea)
    return TeaOut(
        id=tea.id,
        name=tea.name,
        category=tea.category,
        year=tea.year,
        origin=tea.origin,
        spec=tea.spec,
        price_min=tea.price_min,
        price_max=tea.price_max,
        intro=tea.intro,
        cover_url=tea.cover_url,
        status=tea.status,
        weight=tea.weight,
        created_at=tea.created_at,
        updated_at=tea.updated_at,
    )


@router.put("/teas/{tea_id}", response_model=TeaOut, dependencies=[Depends(require_admin)])
def admin_update_tea(tea_id: int, body: TeaBase, db: Session = Depends(get_db)):
    tea = db.get(Tea, tea_id)
    if not tea:
        raise HTTPException(status_code=404, detail={"code": "not_found", "message": "tea not found"})

    tea.name = body.name
    tea.category = body.category
    tea.year = body.year
    tea.origin = body.origin
    tea.spec = body.spec
    tea.price_min = body.price_min
    tea.price_max = body.price_max
    tea.intro = body.intro
    tea.cover_url = body.cover_url
    tea.status = body.status
    tea.weight = body.weight
    tea.updated_at = datetime.utcnow()

    db.add(tea)
    db.commit()
    db.refresh(tea)

    return TeaOut(
        id=tea.id,
        name=tea.name,
        category=tea.category,
        year=tea.year,
        origin=tea.origin,
        spec=tea.spec,
        price_min=tea.price_min,
        price_max=tea.price_max,
        intro=tea.intro,
        cover_url=tea.cover_url,
        status=tea.status,
        weight=tea.weight,
        created_at=tea.created_at,
        updated_at=tea.updated_at,
    )


@router.delete("/teas/{tea_id}", dependencies=[Depends(require_admin)])
def admin_delete_tea(tea_id: int, db: Session = Depends(get_db)):
    tea = db.get(Tea, tea_id)
    if not tea:
        raise HTTPException(status_code=404, detail={"code": "not_found", "message": "tea not found"})

    db.delete(tea)
    db.commit()
    return {"ok": True}


@router.post("/upload", dependencies=[Depends(require_admin)])
def admin_upload(file: UploadFile = File(...)):
    uploads_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "uploads")
    os.makedirs(uploads_dir, exist_ok=True)

    ext = os.path.splitext(file.filename or "")[1].lower() or ".bin"
    name = f"{uuid4().hex}{ext}"
    path = os.path.join(uploads_dir, name)

    content = file.file.read()
    with open(path, "wb") as f:
        f.write(content)

    return {"url": f"/uploads/{name}"}


@router.post("/import/excel", response_model=ImportPreviewOut, dependencies=[Depends(require_admin)])
def import_excel(file: UploadFile = File(...)):
    df = pd.read_excel(file.file)

    required = ["名称", "分类", "年份", "产地", "规格", "主图URL"]
    cols = list(df.columns)
    missing = [c for c in required if c not in cols]
    if missing:
        raise HTTPException(status_code=400, detail={"code": "bad_request", "message": f"missing columns: {missing}"})

    rows: List[ImportPreviewRow] = []
    for idx, row in df.iterrows():
        errors: List[str] = []
        name = str(row.get("名称") or "").strip()
        category = str(row.get("分类") or "").strip()
        origin = str(row.get("产地") or "").strip()
        spec = str(row.get("规格") or "").strip()
        cover_url = str(row.get("主图URL") or "").strip()

        year_raw = row.get("年份")
        try:
            year = int(year_raw)
        except Exception:
            year = 0

        if not name:
            errors.append("名称必填")
        if not category:
            errors.append("分类必填")
        if year <= 0:
            errors.append("年份必须为数字")
        if not origin:
            errors.append("产地必填")
        if not spec:
            errors.append("规格必填")
        if not cover_url:
            errors.append("主图URL必填")

        if errors:
            rows.append(ImportPreviewRow(index=int(idx), ok=False, errors=errors, data=None))
            continue

        base = TeaBase(
            name=name,
            category=category,
            year=year,
            origin=origin,
            spec=spec,
            price_min=int(row.get("价格下限")) if str(row.get("价格下限") or "").strip() else None,
            price_max=int(row.get("价格上限")) if str(row.get("价格上限") or "").strip() else None,
            intro=str(row.get("简介") or "").strip() or None,
            cover_url=cover_url,
            status="online",
            weight=0,
        )
        rows.append(ImportPreviewRow(index=int(idx), ok=True, errors=[], data=base))

    return ImportPreviewOut(columns=cols, rows=rows, total_rows=len(df.index))


@router.post("/import/commit", dependencies=[Depends(require_admin)])
def import_commit(body: ImportCommitIn, db: Session = Depends(get_db)):
    now = datetime.utcnow()
    ok = 0
    for item in body.items:
        tea = Tea(
            name=item.name,
            category=item.category,
            year=item.year,
            origin=item.origin,
            spec=item.spec,
            price_min=item.price_min,
            price_max=item.price_max,
            intro=item.intro,
            cover_url=item.cover_url,
            status=item.status,
            weight=item.weight,
            created_at=now,
            updated_at=now,
        )
        db.add(tea)
        ok += 1

    db.commit()
    return {"ok": True, "inserted": ok}


def _parse_range(from_: Optional[str], to: Optional[str]):
    if not from_ and not to:
        return None, None

    if not from_ or not to:
        raise HTTPException(status_code=400, detail={"code": "bad_request", "message": "from/to required"})

    try:
        start = datetime.strptime(from_, "%Y-%m-%d")
        end = datetime.strptime(to, "%Y-%m-%d")
    except Exception:
        raise HTTPException(status_code=400, detail={"code": "bad_request", "message": "invalid date"})

    if end < start:
        raise HTTPException(status_code=400, detail={"code": "bad_request", "message": "invalid range"})

    # end 为当天 23:59:59 的上界：用 +1 day 的开区间
    end_exclusive = end + pd.Timedelta(days=1)
    return start, end_exclusive.to_pydatetime()


@router.get("/dashboard/summary", response_model=DashboardSummaryOut, dependencies=[Depends(require_admin)])
def dashboard_summary(from_: Optional[str] = None, to: Optional[str] = None, db: Session = Depends(get_db)):
    start, end = _parse_range(from_, to)

    ev_q = select(func.count()).select_from(Event).where(Event.type == "impression")
    fb_like_q = select(func.count()).select_from(Feedback).where(Feedback.action == "like")
    fb_dislike_q = select(func.count()).select_from(Feedback).where(Feedback.action == "dislike")

    if start and end:
        ev_q = ev_q.where(Event.created_at >= start).where(Event.created_at < end)
        fb_like_q = fb_like_q.where(Feedback.created_at >= start).where(Feedback.created_at < end)
        fb_dislike_q = fb_dislike_q.where(Feedback.created_at >= start).where(Feedback.created_at < end)

    pv = db.execute(ev_q).scalar_one()
    likes = db.execute(fb_like_q).scalar_one()
    dislikes = db.execute(fb_dislike_q).scalar_one()
    like_rate = (likes / pv) if pv else None
    return DashboardSummaryOut(pv=pv, likes=likes, dislikes=dislikes, like_rate=like_rate)


@router.get("/dashboard/rank", response_model=DashboardRankOut, dependencies=[Depends(require_admin)])
def dashboard_rank(sort: str = "like_rate", from_: Optional[str] = None, to: Optional[str] = None, db: Session = Depends(get_db)):
    start, end = _parse_range(from_, to)

    teas = db.execute(select(Tea).where(Tea.status == "online")).scalars().all()

    items: List[DashboardRankRow] = []
    for t in teas:
        pv_q = select(func.count()).select_from(Event).where(Event.tea_id == t.id).where(Event.type == "impression")
        like_q = select(func.count()).select_from(Feedback).where(Feedback.tea_id == t.id).where(Feedback.action == "like")
        dislike_q = select(func.count()).select_from(Feedback).where(Feedback.tea_id == t.id).where(Feedback.action == "dislike")

        if start and end:
            pv_q = pv_q.where(Event.created_at >= start).where(Event.created_at < end)
            like_q = like_q.where(Feedback.created_at >= start).where(Feedback.created_at < end)
            dislike_q = dislike_q.where(Feedback.created_at >= start).where(Feedback.created_at < end)

        pv = db.execute(pv_q).scalar_one()
        likes = db.execute(like_q).scalar_one()
        dislikes = db.execute(dislike_q).scalar_one()
        like_rate = (likes / pv) if pv else None

        items.append(
            DashboardRankRow(
                tea=TeaOut(
                    id=t.id,
                    name=t.name,
                    category=t.category,
                    year=t.year,
                    origin=t.origin,
                    spec=t.spec,
                    price_min=t.price_min,
                    price_max=t.price_max,
                    intro=t.intro,
                    cover_url=t.cover_url,
                    status=t.status,
                    weight=t.weight,
                    created_at=t.created_at,
                    updated_at=t.updated_at,
                ),
                pv=pv,
                likes=likes,
                dislikes=dislikes,
                like_rate=like_rate,
            )
        )

    if sort == "created_at":
        items.sort(key=lambda x: x.tea.created_at, reverse=True)
    else:
        items.sort(key=lambda x: (x.like_rate or 0.0), reverse=True)

    return DashboardRankOut(items=items)


@router.get("/dashboard/trend", dependencies=[Depends(require_admin)])
def dashboard_trend(from_: str, to: str, db: Session = Depends(get_db)):
    start, end = _parse_range(from_, to)

    if not start or not end:
        raise HTTPException(status_code=400, detail={"code": "bad_request", "message": "from/to required"})

    # SQLite 的 date() 输出 YYYY-MM-DD
    pv_rows = db.execute(
        select(func.date(Event.created_at).label("d"), func.count())
        .select_from(Event)
        .where(Event.type == "impression")
        .where(Event.created_at >= start)
        .where(Event.created_at < end)
        .group_by("d")
    ).all()

    like_rows = db.execute(
        select(func.date(Feedback.created_at).label("d"), func.count())
        .select_from(Feedback)
        .where(Feedback.action == "like")
        .where(Feedback.created_at >= start)
        .where(Feedback.created_at < end)
        .group_by("d")
    ).all()

    dislike_rows = db.execute(
        select(func.date(Feedback.created_at).label("d"), func.count())
        .select_from(Feedback)
        .where(Feedback.action == "dislike")
        .where(Feedback.created_at >= start)
        .where(Feedback.created_at < end)
        .group_by("d")
    ).all()

    pv_map = {d: c for d, c in pv_rows}
    like_map = {d: c for d, c in like_rows}
    dislike_map = {d: c for d, c in dislike_rows}

    points = []
    cursor = start
    while cursor < end:
        d = cursor.strftime("%Y-%m-%d")
        points.append({"date": d, "pv": int(pv_map.get(d, 0)), "likes": int(like_map.get(d, 0)), "dislikes": int(dislike_map.get(d, 0))})
        cursor = cursor + pd.Timedelta(days=1)

    return {"points": points}
