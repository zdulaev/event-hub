import os
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL") # e.g. postgresql+psycopg2://user:pass@timescaledb:5432/dbname