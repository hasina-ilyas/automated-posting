from __future__ import annotations
"""Bluesky AT Protocol integration.

Docs:
- https://docs.bsky.app/docs/api/com-atproto-server-create-session
- https://docs.bsky.app/docs/api/com-atproto-repo-create-record
"""

from datetime import datetime, timezone

import httpx

from app.config import Settings
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult


class BlueskyPlatform(BasePlatform):
    name = "Bluesky"

    def __init__(self, settings: Settings) -> None:
        self.handle = settings.bluesky_handle
        self.app_password = settings.bluesky_app_password
        self.pds_url = settings.bluesky_pds_url.rstrip("/")

    async def post(self, message: str) -> PlatformResult:
        if not self.handle or not self.app_password:
            return self.failure("Missing BLUESKY_HANDLE or BLUESKY_APP_PASSWORD")

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                session_response = await client.post(
                    f"{self.pds_url}/xrpc/com.atproto.server.createSession",
                    json={"identifier": self.handle, "password": self.app_password},
                )

                if session_response.status_code >= 400:
                    return self.failure(
                        f"Bluesky auth failed: {session_response.text}"
                    )

                session = session_response.json()
                access_jwt = session["accessJwt"]
                did = session["did"]
                handle = session.get("handle", self.handle)

                created_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                record = {
                    "$type": "app.bsky.feed.post",
                    "text": message,
                    "createdAt": created_at,
                }

                create_response = await client.post(
                    f"{self.pds_url}/xrpc/com.atproto.repo.createRecord",
                    headers={"Authorization": f"Bearer {access_jwt}"},
                    json={
                        "repo": did,
                        "collection": "app.bsky.feed.post",
                        "record": record,
                    },
                )

                if create_response.status_code >= 400:
                    return self.failure(
                        f"Bluesky post failed: {create_response.text}"
                    )

                data = create_response.json()
                uri = data.get("uri", "")
                # at://did:plc:xxx/app.bsky.feed.post/rkey → https://bsky.app/profile/handle/post/rkey
                rkey = uri.rsplit("/", 1)[-1] if uri else None
                posted_url = (
                    f"https://bsky.app/profile/{handle}/post/{rkey}" if rkey else uri
                )
                return self.success(posted_url, public_access=True)
        except httpx.HTTPError as exc:
            return self.failure(f"Bluesky request failed: {exc}")
        except KeyError as exc:
            return self.failure(f"Bluesky unexpected response: missing {exc}")
