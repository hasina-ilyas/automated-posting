from __future__ import annotations
"""Telegram Bot API integration.

Docs: https://core.telegram.org/bots/api#sendmessage
"""

import httpx

from app.config import Settings
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult


class TelegramPlatform(BasePlatform):
    name = "Telegram"

    def __init__(self, settings: Settings) -> None:
        self.bot_token = settings.telegram_bot_token
        self.chat_id = settings.telegram_chat_id

    async def post(self, message: str) -> PlatformResult:
        if not self.bot_token or not self.chat_id:
            return self.failure("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID")

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "disable_web_page_preview": False,
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload)
                data = response.json()

            if response.status_code >= 400 or not data.get("ok"):
                description = data.get("description") or response.text
                return self.failure(f"Telegram API error: {description}")

            result = data.get("result", {})
            message_id = result.get("message_id")
            chat = result.get("chat", {})
            username = chat.get("username")

            if username and message_id:
                posted_url = f"https://t.me/{username}/{message_id}"
                public = True
            else:
                posted_url = f"telegram://chat/{self.chat_id}/message/{message_id}"
                public = False

            return self.success(posted_url, public_access=public)
        except httpx.HTTPError as exc:
            return self.failure(f"Telegram request failed: {exc}")
