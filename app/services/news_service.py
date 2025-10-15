# app/services/news_service.py
from typing import List, Dict, Any, Optional
from sqlalchemy import create_engine, text
from app.core.config import settings

# SQLAlchemy 엔진 (필요 시 모듈 공용으로 빼도 됨)
def _engine():
    url = (
        f"postgresql+psycopg2://{settings.DB_USER}:{settings.DB_PASSWORD}"
        f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    )
    # 연결 체크/재시도 안정성 향상 옵션
    return create_engine(url, pool_pre_ping=True)

def fetch_news_today_kst(
    keyword: str,
    limit: int = 50,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    """
    news 테이블에서 keyword 일치/포함 + pub_date가 '한국시간 오늘'인 행만 조회
    """
    sql = text("""
        SELECT id, keyword, title, link, description, pub_date, created_at
        FROM news
        WHERE (keyword = :kw OR keyword ILIKE :kw_like)
          AND (pub_date AT TIME ZONE 'Asia/Seoul')::date
              = (now() AT TIME ZONE 'Asia/Seoul')::date
        ORDER BY pub_date DESC, id DESC
        LIMIT :limit OFFSET :offset
    """)
    params = {
        "kw": keyword,
        "kw_like": f"%{keyword}%",
        "limit": int(limit),
        "offset": int(offset),
    }
    eng = _engine()
    with eng.connect() as conn:
        rows = conn.execute(sql, params).mappings().all()
        return [dict(r) for r in rows]
