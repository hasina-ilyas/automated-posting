from __future__ import annotations
"""Mastodon statuses API integration.

Docs: https://docs.joinmastodon.org/methods/statuses/#create
"""

import httpx

from app.config import Settings
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult


class MastodonPlatform(BasePlatform):
    name = "Mastodon"

    def __init__(self, settings: Settings) -> None:
        self.base_url = settings.mastodon_base_url.rstrip("/")
        self.access_token = settings.mastodon_access_token

    async def post(self, message: str) -> PlatformResult:
        if not self.access_token:
            return self.failure("Missing MASTODON_ACCESS_TOKEN")

        url = f"{self.base_url}/api/v1/statuses"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        payload = {"status": message, "visibility": "public"}

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=headers, data=payload)

            if response.status_code >= 400:
                return self.failure(f"Mastodon API error: {response.text}")

            data = response.json()
            posted_url = data.get("url") or data.get("uri")
            return self.success(posted_url, public_access=True)
        except httpx.HTTPError as exc:
            return self.failure(f"Mastodon request failed: {exc}")
