import logging
from logging.handlers import RotatingFileHandler
import sys

def setup_logger(level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger("app")
    if logger.handlers:  # 중복 추가 방지
        return logger

    logger.setLevel(level)

    # 콘솔 출력 핸들러
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    ch.setFormatter(logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))
    logger.addHandler(ch)

    # (선택) 파일 로그: logs/app.log, 5MB * 3개 순환
    fh = RotatingFileHandler("logs/app.log", maxBytes=5_000_000, backupCount=3, encoding="utf-8")
    fh.setLevel(level)
    fh.setFormatter(logging.Formatter(
        "%(asctime)s\t%(levelname)s\t%(name)s\t%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))
    logger.addHandler(fh)

    # SQLAlchemy 쿼리 로그(필요시 INFO로 올리면 쿼리/파라미터 보임)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    return logger
