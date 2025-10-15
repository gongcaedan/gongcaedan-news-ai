# app/services/opinion_service.py
import json, re
from typing import List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ValidationError
from app.services.news_service import fetch_news_today_kst
from app.services.gemini_service import get_gemini_response

class OpinionItem(BaseModel):
    title: str = Field(..., alias="제목")
    pro: str = Field(..., alias="찬성의견")
    con: str = Field(..., alias="반대의견")
    date: datetime = Field(..., alias="날짜")  # 날짜 문자열(YYYY-MM-DD)도 자동 파싱

    class Config:
        populate_by_name = True  # 역매핑 허용
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%d")
        }

def _ensure_json(text: str) -> Any:
    """
    모델 응답에서 JSON만 뽑아 파싱.
    ```json ... ``` 형태여도 처리.
    """
    try:
        return json.loads(text)
    except Exception:
        pass
    # ```json ... ``` 또는 ``` ... ``` 블록 추출
    m = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.S | re.I)
    if m:
        return json.loads(m.group(1))
    # JSON 배열만 남도록 괄호부터 잘라 시도
    m = re.search(r"(\[\s*{[\s\S]*}\s*\])", text)
    if m:
        return json.loads(m.group(1))
    # 최종 실패
    return json.loads(text)  # 에러 발생 유도

def build_prompt(items: List[Dict[str, Any]]) -> str:
    lines = [
        "아래의 오늘자 뉴스들을 읽고, 각 뉴스에 대해 '제목', '찬성의견', '반대의견', '날짜' 필드를 가진 JSON 배열(정확히 6개)을 반환하세요.",
        "중요: 마크다운, 설명, 주석 없이 **순수 JSON**만 출력하세요.",
        "규칙:",
        "1) 항목 수는 정확히 6개",
        "2) '날짜'는 YYYY-MM-DD 형식 (한국시간 기준 pub_date를 사용)",
        "3) '찬성의견'과 '반대의견'은 간결한 한 문장~두 문장",
        "",
        "입력 뉴스:",
    ]
    for i, n in enumerate(items, 1):
        kst_date = None
        # pub_date가 들어온 상태 그대로 사용(서비스에서 이미 '오늘 KST' 필터)
        try:
            dt = n.get("pub_date")
            if isinstance(dt, str):
                # ISO 문자열일 경우
                kst_date = dt[:10]
            elif dt:
                kst_date = dt.date().isoformat()
        except Exception:
            kst_date = ""
        lines.append(
            f"{i}. 제목: {n.get('title','')}\n"
            f"   설명: {n.get('description','')}\n"
            f"   링크: {n.get('link','')}\n"
            f"   날짜(KST): {kst_date}"
        )
    lines.append("")
    lines.append('반환 JSON 예시(형식만 참고, 실제 내용은 입력 뉴스 기반으로 작성):')
    lines.append("""[
  {"제목":"...", "찬성의견":"...", "반대의견":"...", "날짜":"2025-10-15"},
  {"제목":"...", "찬성의견":"...", "반대의견":"...", "날짜":"2025-10-15"},
  {"제목":"...", "찬성의견":"...", "반대의견":"...", "날짜":"2025-10-15"},
  {"제목":"...", "찬성의견":"...", "반대의견":"...", "날짜":"2025-10-15"},
  {"제목":"...", "찬성의견":"...", "반대의견":"...", "날짜":"2025-10-15"},
  {"제목":"...", "찬성의견":"...", "반대의견":"...", "날짜":"2025-10-15"}
]""")
    return "\n".join(lines)

def generate_opinions_for_today(keyword: str, limit: int = 6) -> List[Dict[str, Any]]:
    # 1) 오늘 KST 뉴스 6개 수집
    items = fetch_news_today_kst(keyword=keyword, limit=limit, offset=0)

    # 부족할 때도 정확히 6개만 요구하면 모델이 임의 생성할 수 있으므로,
    # 실제 수가 6개 미만이면 그대로 개수만큼만 요청하도록 처리(또는 6개 미만일 경우 에러)
    if len(items) < limit:
        # 여기서는 "있는 만큼만" 생성하도록 프롬프트를 조정
        limit = len(items)
    sliced = items[:limit]

    if limit == 0:
        return []

    # 2) 프롬프트 구성
    prompt = build_prompt(sliced)

    # 3) 모델 호출
    raw = get_gemini_response(prompt)

    # 4) JSON 파싱
    data = _ensure_json(raw)
    if not isinstance(data, list):
        raise ValueError(f"AI 응답이 배열이 아님: {type(data)}")

    if len(data) != limit:
        # 개수가 다르면 슬라이스/검증으로 방어
        data = data[:limit]

    # 5) Pydantic 검증 및 한글 키로 재직렬화
    result: List[Dict[str, Any]] = []
    for obj in data:
        try:
            item = OpinionItem.model_validate(obj)
            # 한글 키(alias)로 덤프
            result.append(json.loads(item.model_dump_json(by_alias=True)))
        except ValidationError as e:
            # 하나라도 틀리면 간단히 스킵(또는 raise로 전체 실패 처리)
            continue

    return result
