from typing import Any

import httpx
from tenacity import (
    AsyncRetrying,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from ai_project_skeleton.config import Settings


def is_retryable(exception: BaseException) -> bool:
    if isinstance(exception, httpx.TransportError):
        return True

    if isinstance(exception, httpx.HTTPStatusError):
        return exception.response.status_code >= 500

    return False


class APIClient:
    def __init__(self, settings: Settings):
        headers = {}

        if settings.api_key:
            headers["Authorization"] = f"Bearer {settings.api_key.get_secret_value()}"

        self.client = httpx.AsyncClient(
            base_url=settings.api_base_url,
            headers=headers,
            timeout=settings.timeout_seconds,
        )

        self.max_retries = settings.max_retries

    async def get_json(self, path: str) -> Any:
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(self.max_retries + 1),
            wait=wait_exponential(multiplier=1, min=1, max=4),
            retry=retry_if_exception(is_retryable),
            reraise=True,
        ):
            with attempt:
                response = await self.client.get(path)
                response.raise_for_status()
                return response.json()

    async def close(self) -> None:
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()
