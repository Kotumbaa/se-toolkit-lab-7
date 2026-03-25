"""
LMS API client.

Makes HTTP calls to the backend API with Bearer token authentication.
All API keys and URLs come from environment variables.
"""

import os
from typing import Any, Optional

import httpx


class LMSAPIClient:
    """Client for the LMS backend API."""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._client: Optional[httpx.Client] = None

    @classmethod
    def from_env(cls) -> "LMSAPIClient":
        """Create client from environment variables."""
        base_url = os.getenv("LMS_API_BASE_URL", "http://localhost:42002")
        api_key = os.getenv("LMS_API_KEY", "")
        return cls(base_url=base_url, api_key=api_key)

    def _get_client(self) -> httpx.Client:
        """Get or create HTTP client with auth headers."""
        if self._client is None:
            self._client = httpx.Client(
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10.0,
            )
        return self._client

    def get_items(self) -> list[dict[str, Any]]:
        """Fetch all items (labs and tasks)."""
        client = self._get_client()
        response = client.get(f"{self.base_url}/items/")
        response.raise_for_status()
        return response.json()

    def get_pass_rates(self, lab: str) -> list[dict[str, Any]]:
        """Fetch pass rates for a specific lab."""
        client = self._get_client()
        response = client.get(
            f"{self.base_url}/analytics/pass-rates",
            params={"lab": lab},
        )
        response.raise_for_status()
        return response.json()

    def health_check(self) -> dict[str, Any]:
        """Check if backend is healthy by fetching items count."""
        items = self.get_items()
        return {"healthy": True, "items_count": len(items)}
