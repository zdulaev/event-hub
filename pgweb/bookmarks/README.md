Создай тут файл default.toml с содержимым:
[[bookmark]]
name = "timescale"
url = "postgres://{POSTGRES_USER}:{POSTGRES_PASSWORD}@$timescaledb:5432/{POSTGRES_DB}?sslmode=disable"
