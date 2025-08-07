from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from src.config import DATABASE_URL
from src.models import metadata

Engine = None
SessionLocal = None

def init_db(url: str = None):
    """ Инициализирует подключение к базе данных.
    :param url: URL подключения к базе данных. Если не указан, используется DATABASE_URL из config.
    :return: Экземпляр SQLAlchemy Engine.
    """
    global Engine, SessionLocal
    db_url = url or DATABASE_URL
    Engine = create_engine(db_url, echo=False)
    SessionLocal = sessionmaker(bind=Engine)

    # Создать таблицы, если их нет
    try:
        metadata.create_all(bind=Engine)
    except Exception as e:
        print(f"[DB INIT] Не удалось создать таблицы: {e}")
    return Engine