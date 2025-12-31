from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class TeaBase(BaseModel):
    name: str
    category: str
    year: int
    origin: str
    spec: str
    price_min: Optional[int] = None
    price_max: Optional[int] = None
    intro: Optional[str] = None
    cover_url: str
    status: str = Field(default="online")
    weight: int = 0


class TeaOut(TeaBase):
    id: int
    created_at: datetime
    updated_at: datetime


class TeaListOut(BaseModel):
    items: List[TeaOut]
    page: int
    page_size: int
    total: int


class EventIn(BaseModel):
    anon_user_id: str
    tea_id: int
    type: str


class FeedbackIn(BaseModel):
    anon_user_id: str
    tea_id: int
    action: str


class MessageFeedbackIn(BaseModel):
    anon_user_id: str
    message: str
    contact: Optional[str] = None
    tea_id: Optional[int] = None


class LoginIn(BaseModel):
    username: str
    password: str


class TokenOut(BaseModel):
    token: str


class ImportPreviewRow(BaseModel):
    index: int
    ok: bool
    errors: List[str]
    data: Optional[TeaBase] = None


class ImportPreviewOut(BaseModel):
    columns: List[str]
    rows: List[ImportPreviewRow]
    total_rows: int


class ImportCommitIn(BaseModel):
    items: List[TeaBase]


class DashboardSummaryOut(BaseModel):
    pv: int
    likes: int
    dislikes: int
    like_rate: Optional[float]


class DashboardRankRow(BaseModel):
    tea: TeaOut
    pv: int
    likes: int
    dislikes: int
    like_rate: Optional[float]


class DashboardRankOut(BaseModel):
    items: List[DashboardRankRow]


class DashboardTrendPoint(BaseModel):
    date: str
    pv: int
    likes: int
    dislikes: int


class DashboardTrendOut(BaseModel):
    points: List[DashboardTrendPoint]
