from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.scheduler import scheduler

# test scheduler import job_fetch_and_store
# from src.scheduler import job_fetch_and_store

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Запуск scheduler при старте приложения
    scheduler.start()

    # test scheduler job
    # await job_fetch_and_store()
    yield
    # Здесь можно добавить graceful shutdown, если нужно
    # scheduler.shutdown()

app = FastAPI(
    title='2019-SDA-OHLCVQ Ingest Service',
    lifespan=lifespan
)

@app.get('/health')
async def health():
    return {'status': 'ok'}