import datetime
import uuid
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, JSON, ARRAY
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy import MetaData, Table

metadata = MetaData()

Log = Table(
    'logs', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('occurred_at', TIMESTAMP(timezone=True), default=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=False),
    Column('service_name', String, nullable=False),
    Column('log_level', String(10), nullable=False),
    Column('message', Text, nullable=False),
    Column('stack_trace', Text),
    Column('request_id', PG_UUID(as_uuid=True), default=uuid.uuid4),
    Column('meta_info', JSON),
    Column('tags', ARRAY(String))
)