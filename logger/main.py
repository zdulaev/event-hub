from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Optional, List
from src.logger import log_error
import traceback

app = FastAPI()

class LogEntry(BaseModel):
    service_name: Optional[str] = None
    level: Optional[str] = None
    message: Optional[str] = ""
    stack_trace: Optional[str] = None
    meta_info: Optional[dict] = {}
    tags: Optional[List[str]] = []

@app.middleware("http")
async def db_logger_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:

        # Логируем и возвращаем 500
        stack = traceback.format_exc()
        log_error(
            service_name='api-service',
            level='ERROR',
            message=str(e),
            stack_trace=stack,
            request_id=None,
            meta_info={'path': request.url.path},
            tags=['exception']
        )
        raise

@app.post("/logs")
async def create_log(entry: LogEntry):
    print(f"Received log entry: {entry}")
    log_error(
        service_name=entry.service_name,
        level=entry.level,
        message=entry.message,
        stack_trace=entry.stack_trace,
        meta_info=entry.meta_info,
        tags=entry.tags
    )
    return {"status": "logged"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}