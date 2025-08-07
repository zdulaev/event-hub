from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import insert as pg_insert
from src.db import SessionLocal
from src.models import ohlcvq, params
from src.client import fetch_ohlcv
from src.client_logger import remote_log
import asyncio
import traceback

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('cron', minute=0, second=1, misfire_grace_time=600)
async def job_fetch_and_store():
    session = SessionLocal()
    try:
        rows = session.execute(params.select()).fetchall()
        if not rows:
            remote_log(
                level='WARNING',
                message="Параметры для получения OHLCV не найдены.",
                meta_info={'job': 'job_fetch_and_store'},
                tags=['scheduler', 'ohlcv']
            )
            return

        now = datetime.now(timezone.utc)
        minutes_passed = now.minute

        for inst, unit, api_key, limit in rows:

            # пауза 1 секунда перед каждым запросом
            await asyncio.sleep(1)

            # Если пошла следующая минута текущего часа, увеличиваем лимит на количество минут, прошедших с начала часа
            actual_limit = int(limit)
            if minutes_passed > 0:
                actual_limit += minutes_passed

            data = await fetch_ohlcv(inst, api_key, actual_limit, unit)

            # Подготовка вставки с проверкой на нулевые объемы
            to_insert = []
            for bar in data:
                if bar.get('VOLUME', 0) == 0 or bar.get('QUOTE_VOLUME', 0) == 0:
                    continue
                to_insert.append({
                    'timestamp': datetime.fromtimestamp(bar['TIMESTAMP'], timezone.utc),
                    'instrument': inst,
                    'unit': unit,
                    'open': bar['OPEN'],
                    'high': bar['HIGH'],
                    'low': bar['LOW'],
                    'close': bar['CLOSE'],
                    'volume': bar['VOLUME'],
                    'quote_volume': bar['QUOTE_VOLUME'],
                })

            # Выполнение вставки в базу данных
            if to_insert:
                stmt = pg_insert(ohlcvq).values(to_insert)
                stmt = stmt.on_conflict_do_nothing(
                    index_elements=['timestamp', 'instrument', 'unit']
                )
                session.execute(stmt)
                session.commit()
            else:
                remote_log(
                    level='WARNING',
                    message=f"Нет данных для вставки для инструмента {inst} и единицы измерения {unit}.",
                    meta_info={'job': 'job_fetch_and_store', 'instrument': inst, 'unit': unit},
                    tags=['scheduler', 'ohlcv']
                )
    except Exception as e:
        session.rollback()
        remote_log(
            level='ERROR',
            message=f"Ошибка в job_fetch_and_store: {e}",
            stack_trace=traceback.format_exc(),
            meta_info={'job': 'job_fetch_and_store'},
            tags=['scheduler', 'ohlcv']
        )
    finally:
        session.close()