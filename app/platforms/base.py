from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Optional

from app.schemas import PlatformResult


class BasePlatform(ABC):
    """Contract for every third-party posting integration."""

    name: str

    @abstractmethod
    async def post(self, message: str) -> PlatformResult:
        """Publish `message` and return a normalized result."""

    def success(
        self,
        posted_url: Optional[str],
        *,
        public_access: bool = True,
        when: Optional[datetime] = None,
    ) -> PlatformResult:
        moment = when or datetime.now(timezone.utc)
        return PlatformResult(
            platform=self.name,
            status="success",
            posted_url=posted_url,
            public_access=public_access,
            date=moment.date(),
            time=moment.time().replace(microsecond=0),
            error=None,
        )

    def failure(self, error: str) -> PlatformResult:
        return PlatformResult(
            platform=self.name,
            status="failed",
            posted_url=None,
            public_access=False,
            date=None,
            time=None,
            error=error,
        )
