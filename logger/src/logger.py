import logging
import uuid
import src.db as db_module
from src.models import Log

# Инициализация БД при импорте (на всякий случай)
db_module.init_db()

# Настройка консольного логгера
logger = logging.getLogger('app_logger')
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setFormatter(
    logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
)
logger.addHandler(console_handler)

def log_error(
    service_name: str,
    level: str,
    message: str,
    stack_trace: str,
    request_id: uuid.UUID = None,
    meta_info: dict = None,
    tags: list = None
):
    """
    Логирует сообщение в консоль и в таблицу logs.
    """
    if not service_name:
        service_name = "unknown_service"
    if not level:
        level = "UNKNOWN"
    if not message:
        message = "No message provided"
    if not stack_trace:
        stack_trace = None
    if not request_id:
        request_id = uuid.uuid4()
    if not meta_info:
        meta_info = {}
    if not isinstance(tags, list):
        tags = []
    
    
    # Приводим уровень к нижнему регистру
    level = level.lower()

    # Лог в консоль
    log_fn = getattr(logger, level, logger.error)
    log_fn(f'{service_name} - {message}', exc_info=(level == 'error'))

    # Лог в БД
    session = db_module.SessionLocal()
    try:
        session.execute(Log.insert().values(
            service_name=service_name,
            log_level=level,
            message=message,
            stack_trace=stack_trace,
            request_id=request_id,
            meta_info=meta_info,
            tags=tags
        ))
        session.commit()
    except Exception as e:
        logger.error(f'Не удалось записать лог в БД: {e}')
        session.rollback()
    finally:
        session.close()