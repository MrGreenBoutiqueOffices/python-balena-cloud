"""Release resource client."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aiohttp.hdrs import METH_DELETE

from balena_cloud.exceptions import BalenaCloudResourceNotFoundError
from balena_cloud.models import Release


@dataclass
class ReleaseResource:
    """Resource client for release related requests."""

    parent: Any

    async def get(self, release_id: int) -> Release:
        """Get a release by its ID.

        Args:
        ----
            release_id: The release ID.

        Returns:
        -------
            A release object.

        """
        response = await self.parent.request(f"release({release_id})")
        if not response["d"]:
            msg = "No release found with the provided ID."
            raise BalenaCloudResourceNotFoundError(msg)
        return Release.from_dict(response["d"][0])

    async def remove(self, release_id: int) -> None:
        """Remove a release.

        Args:
        ----
            release_id: The release ID.

        """
        await self.parent.request(f"release({release_id})", method=METH_DELETE)
