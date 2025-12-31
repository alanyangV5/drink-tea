from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Event, Feedback, MessageFeedback, Tea
from app.schemas import FeedbackIn, MessageFeedbackIn, TeaListOut, TeaOut, EventIn

router = APIRouter(prefix="/api", tags=["public"])


def _today_range() -> Tuple[datetime, datetime]:
    now = datetime.utcnow()
    start = datetime(now.year, now.month, now.day)
    end = start + timedelta(days=1)
    return start, end


@router.get("/teas", response_model=TeaListOut)
def list_teas(
    category: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
    anon_user_id: Optional[str] = None,
    exclude_ids: Optional[str] = None,
    tea_ids: Optional[str] = None,
    db: Session = Depends(get_db),
):
    if page < 1 or page_size < 1 or page_size > 50:
        raise HTTPException(status_code=400, detail={"code": "bad_request", "message": "invalid pagination"})

    exclude: set[int] = set()
    if exclude_ids:
        for x in exclude_ids.split(","):
            x = x.strip()
            if not x:
                continue
            try:
                exclude.add(int(x))
            except ValueError:
                continue

    include: set[int] = set()
    if tea_ids:
        for x in tea_ids.split(","):
            x = x.strip()
            if not x:
                continue
            try:
                include.add(int(x))
            except ValueError:
                continue

    q = select(Tea).where(Tea.status == "online")
    if category:
        q = q.where(Tea.category == category)

    if include:
        q = q.where(Tea.id.in_(include))
    else:
        # 只有在没有指定tea_ids时才排除今日已反馈的茶叶
        if anon_user_id:
            start, end = _today_range()
            sub = (
                select(Feedback.tea_id)
                .where(Feedback.anon_user_id == anon_user_id)
                .where(Feedback.created_at >= start)
                .where(Feedback.created_at < end)
            )
            q = q.where(Tea.id.not_in(sub))

    if exclude:
        q = q.where(Tea.id.not_in(exclude))

    # 排序：weight desc, created_at desc（推荐打分会在后续迭代扩展）
    q = q.order_by(Tea.weight.desc(), Tea.created_at.desc())

    total = db.execute(select(func.count()).select_from(q.subquery())).scalar_one()

    offset = (page - 1) * page_size
    rows = db.execute(q.offset(offset).limit(page_size)).scalars().all()

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


@router.get("/teas/{tea_id}", response_model=TeaOut)
def get_tea(tea_id: int, db: Session = Depends(get_db)):
    tea = db.get(Tea, tea_id)
    if not tea or tea.status != "online":
        raise HTTPException(status_code=404, detail={"code": "not_found", "message": "tea not found"})

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


@router.post("/events")
def post_event(body: EventIn, db: Session = Depends(get_db)):
    ev = Event(anon_user_id=body.anon_user_id, tea_id=body.tea_id, type=body.type)
    db.add(ev)
    db.commit()
    return {"ok": True}


@router.post("/feedback")
def post_feedback(body: FeedbackIn, db: Session = Depends(get_db)):
    if body.action not in ("like", "dislike"):
        raise HTTPException(status_code=400, detail={"code": "bad_request", "message": "invalid action"})

    start, end = _today_range()
    exists = db.execute(
        select(func.count())
        .select_from(Feedback)
        .where(Feedback.anon_user_id == body.anon_user_id)
        .where(Feedback.tea_id == body.tea_id)
        .where(Feedback.created_at >= start)
        .where(Feedback.created_at < end)
    ).scalar_one()

    if exists:
        return {"ok": True, "dedup": True}

    fb = Feedback(anon_user_id=body.anon_user_id, tea_id=body.tea_id, action=body.action)
    db.add(fb)
    db.commit()
    return {"ok": True}


@router.post("/feedback/message")
def post_message_feedback(body: MessageFeedbackIn, db: Session = Depends(get_db)):
    msg = MessageFeedback(
        anon_user_id=body.anon_user_id,
        tea_id=body.tea_id,
        message=body.message,
        contact=body.contact,
    )
    db.add(msg)
    db.commit()
    return {"ok": True}
