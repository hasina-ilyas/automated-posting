from __future__ import annotations
from app.platforms.bluesky import BlueskyPlatform
from app.platforms.devto import DevToPlatform
from app.platforms.discord import DiscordPlatform
from app.platforms.mastodon import MastodonPlatform
from app.platforms.telegram import TelegramPlatform

__all__ = [
    "TelegramPlatform",
    "DiscordPlatform",
    "MastodonPlatform",
    "DevToPlatform",
    "BlueskyPlatform",
]
