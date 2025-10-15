import requests
from app.core.config import settings

# 사용할 최신 모델 (빠른 응답: flash / 고품질: pro)
MODEL = "gemini-2.5-pro"   # 또는 "gemini-1.5-pro", "gemini-1.5-flash-latest"

def get_gemini_response(prompt: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
    headers = {"Content-Type": "application/json"}
    params = {"key": settings.GEMINI_API_KEY}
    data = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ]
    }

    try:
        resp = requests.post(url, headers=headers, params=params, json=data, timeout=30)
        # 에러면 예외 발생시켜 상세 로그 보이게
        resp.raise_for_status()
        j = resp.json()
        # 정상 응답 파싱
        return j["candidates"][0]["content"]["parts"][0]["text"]
    except requests.HTTPError as e:
        # Google 에러 메시지 그대로 전달되게 방어
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text
        raise RuntimeError(f"Gemini API error: {resp.status_code} {detail}") from e
