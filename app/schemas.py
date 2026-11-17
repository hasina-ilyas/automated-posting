from __future__ import annotations

import datetime as dt
import re
from typing import List, Literal, Optional
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator

URL_PATTERN = re.compile(
    r"https?://[^\s<>\"']+",
    re.IGNORECASE,
)


class PostingRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=200)

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        text = value.strip()
        if not text:
            raise ValueError("Message must not be empty")

        if len(text) > 200:
            raise ValueError("Message must not exceed 200 characters")

        urls = URL_PATTERN.findall(text)
        if len(urls) == 0:
            raise ValueError("Message must include exactly one CTA link (http/https URL)")
        if len(urls) > 1:
            raise ValueError("Message must include exactly one CTA link")

        parsed = urlparse(urls[0])
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError(f"Invalid CTA URL: {urls[0]}")

        return text


class PlatformResult(BaseModel):
    platform: str
    status: Literal["success", "failed"]
    posted_url: Optional[str] = None
    public_access: bool = False
    date: Optional[dt.date] = None
    time: Optional[dt.time] = None
    error: Optional[str] = None


class PostingResponse(BaseModel):
    success: bool
    results: List[PlatformResult]
