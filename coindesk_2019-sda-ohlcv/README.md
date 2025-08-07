## Структура проекта

```
2019-sda-ohlcv/
├── Dockerfile
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── main.py            # FastAPI приложение и точка запуска
│   ├── config.py          # Загрузка параметров из env
│   ├── db.py              # Инициализация подключения к TimescaleDB
│   ├── models.py          # SQLAlchemy модели таблиц
│   ├── client.py          # HTTP-клиент для Coindesk Data API
│   ├── scheduler.py       # Background task для планировщика
│   └── utils.py           # Вспомогательные функции
└── .env                   # Секреты и конфиги
```

---

# requirements.txt
```
fastapi
uvicorn[standard]
httpx
SQLAlchemy
psycopg2-binary
alembic            # при необходимости миграций
python-dotenv
APScheduler
```  

---

# Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```  

---

# app/config.py
```python
import os
from dotenv import load_dotenv
load_dotenv()

COINDESK_API_KEY = os.getenv("COINDESK_API_KEY")
DB_DSN = os.getenv("DB_DSN")  # например, postgresql+psycopg2://user:pass@host:5432/dbname
INSTRUMENTS = os.getenv("INSTRUMENTS", "XBX-USD,LNX-USD,XRX-USD,XLMX-USD").split(',')
UNIT = os.getenv("UNIT", "MINUTE")
LIMIT = int(os.getenv("LIMIT", "60"))  # сколько свечей за час
```  

---

# app/db.py
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import DB_DSN

engine = create_engine(DB_DSN, pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(bind=engine)
```  

---

# app/models.py
```python
from sqlalchemy import Table, Column, String, Float, TIMESTAMP, MetaData

metadata = MetaData()

ohlcvq = Table(
    'coindesk_2019_sda_ohlcvq', metadata,
    Column('timestamp', TIMESTAMP(timezone=True), primary_key=True),
    Column('instrument', String(16), primary_key=True),
    Column('unit', String(16), primary_key=True),
    Column('open', Float),
    Column('high', Float),
    Column('low', Float),
    Column('close', Float),
    Column('volume', Float),
    Column('quote_volume', Float),
)
```  

---

# app/client.py
```python
import httpx
from .config import COINDESK_API_KEY, UNIT, LIMIT

BASE_URL = 'https://data-api.coindesk.com/index/cc/v1/historical/minutes'
HEADERS = {'Authorization': f'Apikey {COINDESK_API_KEY}'}

async def fetch_ohlcv(instrument: str) -> list[dict]:
    params = {
        'market': 'sda',
        'instrument': instrument,
        'limit': LIMIT,
        'groups': 'OHLC,VOLUME'
    }
    async with httpx.AsyncClient() as client:
        r = await client.get(BASE_URL, headers=HEADERS, params=params, timeout=30)
        r.raise_for_status()
        data = r.json().get('Data', [])
        return data
```  

---

# app/scheduler.py
```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timezone, timedelta
from .client import fetch_ohlcv
from .db import SessionLocal, engine
from .models import ohlcvq

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('cron', minute=0)
async def job_fetch_and_store():
    # каждый новый час
    ts_now = datetime.now(timezone.utc)
    session = SessionLocal()
    try:
        for inst in __import__('app.config', fromlist=['INSTRUMENTS']).INSTRUMENTS:
            data = await fetch_ohlcv(inst)
            # фильтруем все, кроме полных свеч
            rows = []
            for bar in data:
                if bar['VOLUME'] == 0 or bar['QUOTE_VOLUME'] == 0:
                    continue
                rows.append({
                    'timestamp': datetime.fromtimestamp(bar['TIMESTAMP'], timezone.utc),
                    'instrument': inst,
                    'unit': UNIT,
                    'open': bar['OPEN'],
                    'high': bar['HIGH'],
                    'low': bar['LOW'],
                    'close': bar['CLOSE'],
                    'volume': bar['VOLUME'],
                    'quote_volume': bar['QUOTE_VOLUME'],
                })
            if rows:
                session.execute(ohlcvq.insert().values(rows))
                session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
```  

---

# app/main.py
```python
from fastapi import FastAPI
from .scheduler import scheduler

app = FastAPI(title='2019-SDA-OHLCVQ Ingest Service')

@app.on_event('startup')
async def start_scheduler():
    scheduler.start()

@app.get('/health')
async def health():
    return {'status': 'ok'}
```  

---

**Пояснения**
1. **Cron-задание**: выполнение каждую 0 минуту часа (т.е. сразу после часа).  
2. **Фильтрация**: отбрасываем неполные свечи (VOLUME=0).  
3. **Конфигурация** через `.env` (ключ, список инструментов, DSN).  
4. **Массовая вставка** в TimescaleDB через SQLAlchemy.  

Для развёртывания:  
- Создать секреты в `.env`.  
- Собрать образ: `docker build -t sda-ingest .`  
- Запустить: `docker run -d --env-file .env sda-ingest`  

Готово. Теперь сервис автоматически выгружает и сохраняет минутные свечи каждый час.
