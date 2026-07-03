# api_client.py
import httpx

QUOTABLE_URL = "https://api.quotable.io/random"

async def fetch_quote() -> dict:
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.get(QUOTABLE_URL)
            response.raise_for_status()
            data = response.json()
            return {
                "content": data["content"],
                "author": data["author"]
            }
        except (httpx.HTTPError, httpx.TimeoutException, KeyError):
            return {
                "content": "La créativité est l'intelligence qui s'amuse.",
                "author": "Albert Einstein"
            }