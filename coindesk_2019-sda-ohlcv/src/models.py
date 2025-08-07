from sqlalchemy import Table, Column, String, Float, TIMESTAMP, MetaData
from sqlalchemy.dialects.postgresql import VARCHAR

metadata = MetaData()

ohlcvq = Table(
    'coindesk_2019_sda_ohlcvq', metadata,
    Column('timestamp', TIMESTAMP(timezone=True), primary_key=True),
    Column('instrument', VARCHAR(16), primary_key=True),
    Column('unit', VARCHAR(16), primary_key=True),
    Column('open', Float),
    Column('high', Float),
    Column('low', Float),
    Column('close', Float),
    Column('volume', Float),
    Column('quote_volume', Float),
)

params = Table(
    'coindesk_2019_sda_ohlcvq_params', metadata,
    Column('instrument', VARCHAR(16), primary_key=True),
    Column('unit', VARCHAR(16), primary_key=True, nullable=False, server_default='MINUTE'),
    Column('api_key', String, nullable=False),
    Column('limit', Float, nullable=False, server_default='1000')
)