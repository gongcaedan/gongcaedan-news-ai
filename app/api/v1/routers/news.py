# app/api/v1/routers/news.py
from fastapi import APIRouter, Query, HTTPException
from typing import List, Dict, Any
from app.services.news_service import fetch_news_today_kst
from app.services.opinion_service import generate_opinions_for_today

router = APIRouter(prefix="/api/v1/news", tags=["news"])

@router.get("/today")
def get_today_news(
    kw: str = Query("논란", description="검색할 키워드(기본: 논란)"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    items = fetch_news_today_kst(keyword=kw, limit=limit, offset=offset)
    return {"count": len(items), "items": items}

@router.get("/today/opinions")
def get_today_news_opinions(
    kw: str = Query("논란", description="검색할 키워드(기본: 논란)"),
    count: int = Query(6, ge=1, le=6, description="AI가 생성할 항목 개수(최대 6)")
) -> Dict[str, Any]:
    """
    오늘(KST) 뉴스 중 kw가 일치/포함되는 기사 최대 6개를 가져와
    AI가 아래 스키마로 JSON 배열을 반환:
    { "제목": str, "찬성의견": str, "반대의견": str, "날짜": "YYYY-MM-DD" }
    """
    try:
        items = generate_opinions_for_today(keyword=kw, limit=count)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"opinion generation failed: {e}")

    return {
        "count": len(items),
        "items": items  # 예: [{ "제목": "...", "찬성의견": "...", "반대의견": "...", "날짜": "2025-10-15" }, ...]
    }


