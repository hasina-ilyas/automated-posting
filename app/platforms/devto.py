from __future__ import annotations
"""Dev.to (Forem) articles API integration.

Docs: https://developers.forem.com/api/v1#tag/articles/operation/createArticle
"""

import httpx

from app.config import Settings
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult


class DevToPlatform(BasePlatform):
    name = "Dev.to"

    def __init__(self, settings: Settings) -> None:
        self.api_key = settings.devto_api_key

    async def post(self, message: str) -> PlatformResult:
        if not self.api_key:
            return self.failure("Missing DEVTO_API_KEY")

        url = "https://dev.to/api/articles"
        headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/vnd.forem.api-v1+json",
        }
        payload = {
            "article": {
                "title": message[:80] if len(message) > 10 else f"Update: {message}",
                "body_markdown": message,
                "published": True,
                "tags": ["news", "announcement"],
            }
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=headers, json=payload)

            if response.status_code >= 400:
                return self.failure(f"Dev.to API error: {response.text}")

            data = response.json()
            posted_url = data.get("url")
            return self.success(posted_url, public_access=True)
        except httpx.HTTPError as exc:
            return self.failure(f"Dev.to request failed: {exc}")
