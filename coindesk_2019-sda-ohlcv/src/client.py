import httpx
import traceback
from src.client_logger import remote_log

BASE_URL = 'https://data-api.coindesk.com/index/cc/v1/historical/minutes'

async def fetch_ohlcv(instrument: str, api_key: str, limit: int, unit: str) -> list[dict]:
    headers = {'Authorization': f'Apikey {api_key}'}
    params = {
        'market': 'sda',
        'instrument': instrument,
        'limit': limit,
        'unit': unit,
        'groups': 'OHLC,VOLUME'
    }
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(BASE_URL, headers=headers, params=params, timeout=30)
            r.raise_for_status()
            return r.json().get('Data', [])
        except httpx.HTTPError as e:
            remote_log(
                level='ERROR',
                message=f"Ошибка при получении OHLCV данных: {e}",
                stack_trace=traceback.format_exc(),
                meta_info={'instrument': instrument, 'limit': limit, 'unit': unit},
                tags=['fetch', 'ohlcv']
            )
            return []
        except Exception as e:
            remote_log(
                level='ERROR',
                message=f"Неизвестная ошибка при получении OHLCV данных: {e}",
                stack_trace=traceback.format_exc(),
                meta_info={'instrument': instrument, 'limit': limit, 'unit': unit},
                tags=['fetch', 'ohlcv']
            )
            return []