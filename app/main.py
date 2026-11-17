from __future__ import annotations

from typing import Dict

from fastapi import FastAPI

from app.schemas import PostingRequest, PostingResponse
from app.services.posting_service import PostingService

app = FastAPI(
    title="Automated Multi-Platform Posting System",
    description=(
        "Publishes a short CTA message across Telegram, Discord, Mastodon, "
        "Dev.to, and Bluesky via their official APIs."
    ),
    version="1.0.0",
)


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/posting", response_model=PostingResponse)
async def create_posting(payload: PostingRequest) -> PostingResponse:
    """Validate the message and publish it to all integrated platforms."""
    service = PostingService()
    return await service.publish(payload.message)
