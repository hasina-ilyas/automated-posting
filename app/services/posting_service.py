from __future__ import annotations

import asyncio
import logging
from typing import List, Optional

from app.config import Settings, get_settings
from app.platforms import (
    BlueskyPlatform,
    DevToPlatform,
    DiscordPlatform,
    MastodonPlatform,
    TelegramPlatform,
)
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult, PostingResponse

logger = logging.getLogger(__name__)


class PostingService:
    """Publishes a message to all configured platforms independently."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()
        self.platforms: List[BasePlatform] = [
            TelegramPlatform(self.settings),
            DiscordPlatform(self.settings),
            MastodonPlatform(self.settings),
            DevToPlatform(self.settings),
            BlueskyPlatform(self.settings),
        ]

    async def publish(self, message: str) -> PostingResponse:
        tasks = [self._safe_post(platform, message) for platform in self.platforms]
        results = await asyncio.gather(*tasks)
        overall_success = any(result.status == "success" for result in results)
        return PostingResponse(success=overall_success, results=list(results))

    async def _safe_post(
        self, platform: BasePlatform, message: str
    ) -> PlatformResult:
        try:
            return await platform.post(message)
        except Exception as exc:  # noqa: BLE001 — isolate platform failures
            logger.exception("Unexpected error posting to %s", platform.name)
            return platform.failure(f"Unexpected error: {exc}")
