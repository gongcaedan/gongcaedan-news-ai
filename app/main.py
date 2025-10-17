from fastapi import FastAPI
from app.services.gemini_service import get_gemini_response
from app.api.v1.routers.news import router as news_router  # ✅ 추가

app = FastAPI()

# 뉴스 관련 라우터 등록
app.include_router(news_router)

# Gemini 테스트 엔드포인트
@app.get("/gemini")
def query_gemini(prompt: str):
    return {"response": get_gemini_response(prompt)}

# 헬스체크용
@app.get("/healthz")
def healthz():
    return {"status": "ok"}
