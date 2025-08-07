import requests
import logging
from src.config import LOGGING_URL, SERVICE_NAME

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def remote_log(level, message, stack_trace=None, meta_info=None, tags=None):
    payload = {
        "service_name": SERVICE_NAME,
        "level": level,
        "message": message,
        "stack_trace": stack_trace,
        "meta_info": meta_info or {},
        "tags": tags or []
    }
    try:
        resp = requests.post(LOGGING_URL, json=payload, timeout=2)
        resp.raise_for_status()

        logger_msg = f"service_name={SERVICE_NAME}, level={level}, message={message}, stack_trace={stack_trace}, meta_info={meta_info or {}}, tags={tags or []}"

        if level and level.lower() == 'error':
            logger.error(logger_msg)
        elif level and level.lower() == 'info':
            logger.info(logger_msg)
        elif level and level.lower() == 'debug':
            logger.debug(logger_msg)
        elif level and level.lower() == 'warning':
            logger.warning(logger_msg)
        elif level and level.lower() == 'critical':
            logger.critical(logger_msg)
        else:
            print(logger_msg)

    except Exception as e:
        # на случай, если логирование по сети упало
        logger.error(f"Ошибка при удалённом логировании: {e}")