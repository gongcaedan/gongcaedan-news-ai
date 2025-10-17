FROM python:3.12-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app

# FastAPI 실행 (uvicorn)
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8080"]
