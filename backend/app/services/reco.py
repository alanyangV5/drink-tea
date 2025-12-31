from __future__ import annotations

from datetime import datetime, timedelta


def laplace_like_rate(likes: int, pv: int) -> float:
    # (likes+1)/(pv+2) 避免冷启动极端
    return (likes + 1) / (pv + 2)


def recency_boost(created_at: datetime) -> float:
    # 近7天轻微加成
    days = (datetime.utcnow() - created_at).days
    if days <= 7:
        return 0.15
    if days <= 30:
        return 0.05
    return 0.0
