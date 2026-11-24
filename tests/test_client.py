import httpx
import pytest
import respx

from ai_project_skeleton.client import APIClient
from ai_project_skeleton.config import Settings

BASE_URL = "https://test.local"


@pytest.mark.asyncio
@respx.mock
async def test_successful_request():
    respx.get(f"{BASE_URL}/test").mock(
        return_value=httpx.Response(200, json={"status": "success"})
    )

    settings = Settings(api_base_url=BASE_URL, api_key="test-key")

    async with APIClient(settings) as client:
        result = await client.get_json("/test")

    assert result == {"status": "success"}


@pytest.mark.asyncio
@respx.mock
async def test_retry_success():
    route = respx.get(f"{BASE_URL}/test").mock(
        side_effect=[
            httpx.Response(503),
            httpx.Response(200, json={"status": "recovered"}),
        ]
    )

    settings = Settings(api_base_url=BASE_URL, max_retries=1)

    async with APIClient(settings) as client:
        result = await client.get_json("/test")

    assert result == {"status": "recovered"}
    assert route.call_count == 2


@pytest.mark.asyncio
@respx.mock
async def test_no_retry_on_404():
    route = respx.get(f"{BASE_URL}/missing").mock(return_value=httpx.Response(404))

    settings = Settings(api_base_url=BASE_URL, max_retries=3)

    async with APIClient(settings) as client:
        with pytest.raises(httpx.HTTPStatusError):
            await client.get_json("/missing")

    assert route.call_count == 1


@pytest.mark.asyncio
@respx.mock
async def test_retry_exhausted():
    route = respx.get(f"{BASE_URL}/test").mock(return_value=httpx.Response(503))

    settings = Settings(api_base_url=BASE_URL, max_retries=2)

    async with APIClient(settings) as client:
        with pytest.raises(httpx.HTTPStatusError):
            await client.get_json("/test")

    assert route.call_count == 3
