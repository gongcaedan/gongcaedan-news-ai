# 베이스 이미지
FROM python:3.12-slim

# 작업 디렉토리
WORKDIR /app

# 종속성 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 복사
COPY . .

# 실행 명령
CMD ["python", "main.py"]