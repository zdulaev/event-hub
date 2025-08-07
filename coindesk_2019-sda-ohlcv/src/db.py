from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models import metadata
from src.config import DATABASE_URL

# Инициализация БД и создание таблиц, если их нет
engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=20)
metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)