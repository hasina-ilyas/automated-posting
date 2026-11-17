from __future__ import annotations
from datetime import date, time
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import app
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult, PostingRequest, PostingResponse
from app.services.posting_service import PostingService

client = TestClient(app)


class TestPostingRequestValidation:
    def test_valid_message_with_single_url(self) -> None:
        payload = PostingRequest(
            message="Grow your visibility today. https://example.com"
        )
        assert "https://example.com" in payload.message

    def test_rejects_message_over_200_chars(self) -> None:
        long_text = ("x" * 180) + " https://example.com/path"
        assert len(long_text) > 200
        with pytest.raises(ValidationError) as exc:
            PostingRequest(message=long_text)
        assert "200" in str(exc.value)

    def test_rejects_message_without_url(self) -> None:
        with pytest.raises(ValidationError) as exc:
            PostingRequest(message="Hello world without a link")
        assert "exactly one CTA link" in str(exc.value)

    def test_rejects_message_with_multiple_urls(self) -> None:
        with pytest.raises(ValidationError) as exc:
            PostingRequest(
                message="Check https://one.com and also https://two.com"
            )
        assert "exactly one CTA link" in str(exc.value)

    def test_rejects_empty_message(self) -> None:
        with pytest.raises(ValidationError):
            PostingRequest(message="   ")


class TestPostingEndpoint:
    def test_posting_validation_error_response(self) -> None:
        response = client.post("/posting", json={"message": "no link here"})
        assert response.status_code == 422

    def test_posting_success_shape(self) -> None:
        fake_results = [
            PlatformResult(
                platform="Telegram",
                status="success",
                posted_url="https://t.me/channel/1",
                public_access=True,
                date=date(2026, 11, 15),
                time=time(10, 30, 0),
                error=None,
            ),
            PlatformResult(
                platform="Discord",
                status="failed",
                posted_url=None,
                public_access=False,
                date=None,
                time=None,
                error="Missing DISCORD_WEBHOOK_URL",
            ),
        ]
        mock_response = PostingResponse(success=True, results=fake_results)

        with patch.object(
            PostingService, "publish", new=AsyncMock(return_value=mock_response)
        ):
            response = client.post(
                "/posting",
                json={
                    "message": (
                        "Check out our latest business platform and grow "
                        "your online visibility. https://example.com"
                    )
                },
            )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert len(body["results"]) == 2
        assert body["results"][0]["platform"] == "Telegram"
        assert body["results"][0]["status"] == "success"
        assert body["results"][1]["status"] == "failed"

    def test_health(self) -> None:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class StubPlatform(BasePlatform):
    name = "Stub"

    def __init__(self, result: PlatformResult) -> None:
        self._result = result

    async def post(self, message: str) -> PlatformResult:
        return self._result


@pytest.mark.asyncio
async def test_posting_service_continues_when_one_platform_fails() -> None:
    service = PostingService()
    service.platforms = [
        StubPlatform(
            PlatformResult(
                platform="A",
                status="failed",
                error="boom",
            )
        ),
        StubPlatform(
            PlatformResult(
                platform="B",
                status="success",
                posted_url="https://example.com/b",
                public_access=True,
                date=date(2026, 11, 15),
                time=time(12, 0, 0),
            )
        ),
    ]

    response = await service.publish("Hello https://example.com")
    assert response.success is True
    assert response.results[0].status == "failed"
    assert response.results[1].status == "success"


@pytest.mark.asyncio
async def test_platforms_without_credentials_fail_gracefully() -> None:
    service = PostingService()
    response = await service.publish(
        "Check out our platform. https://example.com"
    )
    assert len(response.results) == 5
    assert all(result.status == "failed" for result in response.results)
    assert all(result.error for result in response.results)
