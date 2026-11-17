from __future__ import annotations
"""Discord Incoming Webhook integration.

Docs: https://discord.com/developers/docs/resources/webhook#execute-webhook
"""

import httpx

from app.config import Settings
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult


class DiscordPlatform(BasePlatform):
    name = "Discord"

    def __init__(self, settings: Settings) -> None:
        self.webhook_url = settings.discord_webhook_url

    async def post(self, message: str) -> PlatformResult:
        if not self.webhook_url:
            return self.failure("Missing DISCORD_WEBHOOK_URL")

        payload = {
            "content": message,
            "allowed_mentions": {"parse": []},
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.webhook_url,
                    params={"wait": "true"},
                    json=payload,
                )

            if response.status_code >= 400:
                return self.failure(f"Discord API error: {response.text}")

            data = response.json() if response.content else {}
            message_id = data.get("id")
            channel_id = data.get("channel_id")

            posted_url = None
            if channel_id and message_id:
                posted_url = f"https://discord.com/channels/@me/{channel_id}/{message_id}"

            return self.success(posted_url, public_access=False)
        except httpx.HTTPError as exc:
            return self.failure(f"Discord request failed: {exc}")
