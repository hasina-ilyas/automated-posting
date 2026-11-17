from __future__ import annotations
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Telegram Bot API — https://core.telegram.org/bots/api
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    # Discord Incoming Webhook — https://discord.com/developers/docs/resources/webhook
    discord_webhook_url: str = ""

    # Mastodon — https://docs.joinmastodon.org/methods/statuses/
    mastodon_base_url: str = "https://mastodon.social"
    mastodon_access_token: str = ""

    # Dev.to — https://developers.forem.com/api/v1#tag/articles/operation/createArticle
    devto_api_key: str = ""

    # Bluesky AT Protocol — https://docs.bsky.app/docs/api/com-atproto-repo-create-record
    bluesky_handle: str = ""
    bluesky_app_password: str = ""
    bluesky_pds_url: str = "https://bsky.social"


@lru_cache
def get_settings() -> Settings:
    return Settings()
