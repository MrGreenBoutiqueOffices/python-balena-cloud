"""Organization resource client."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from balena_cloud.exceptions import (
    BalenaCloudParameterValidationError,
    BalenaCloudResourceNotFoundError,
)
from balena_cloud.models import Fleet, Organization


@dataclass
class OrganizationResource:
    """Resource client for organization related requests."""

    parent: Any

    async def get_all(self) -> list[Organization]:
        """Get all organizations that is authorized by the user.

        Returns
        -------
            A list of organizations.

        """
        response = await self.parent.request("organization")
        return [Organization.from_dict(item) for item in response["d"]]

    async def get(
        self,
        org_id: int | None = None,
        org_handle: str | None = None,
    ) -> Organization:
        """Get an organization by its ID or handle.

        Args:
        ----
            org_id: The organization ID (optional).
            org_handle: The organization handle (optional).

        Returns:
        -------
            An organization object.

        """
        if org_id is None and org_handle is None:
            msg = "You must provide either an organization ID or handle."
            raise BalenaCloudParameterValidationError(msg)

        if org_id is not None:
            response = await self.parent.request(f"organization({org_id})")
        else:
            response = await self.parent.request(f"organization(handle='{org_handle}')")
        if not response["d"]:
            msg = "No organization found with the provided ID or handle."
            raise BalenaCloudResourceNotFoundError(msg)
        return Organization.from_dict(response["d"][0])

    async def get_fleets(self, org_handle: str) -> list[Fleet]:
        """Get all fleets from an organization.

        Args:
        ----
            org_handle: The organization handle.

        Returns:
        -------
            A list of organization fleets.

        """
        response = await self.parent.request(
            "application",
            params={"$filter": f"organization/any(o:o/handle eq '{org_handle}')"},
        )
        return [Fleet.from_dict(item) for item in response["d"]]
