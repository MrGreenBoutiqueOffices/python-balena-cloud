"""Asynchronous Python client for Balena Cloud."""

from __future__ import annotations

import asyncio
import socket
from dataclasses import dataclass
from importlib import metadata
from typing import Any, Self

from aiohttp import ClientError, ClientResponseError, ClientSession
from aiohttp.hdrs import METH_DELETE, METH_GET, METH_PATCH, METH_POST
from yarl import URL

from .exceptions import (
    BalenaCloudAuthenticationError,
    BalenaCloudConnectionError,
    BalenaCloudError,
    BalenaCloudParameterValidationError,
    BalenaCloudResourceNotFoundError,
)
from .models import Device, EnvironmentVariable, Fleet, Organization, Tag

VERSION = metadata.version(__package__)


@dataclass
class BalenaCloud:
    """Main class for handling connections with the Balena Cloud API."""

    token: str

    request_timeout: float = 10.0
    session: ClientSession | None = None

    _close_session: bool = False

    async def _request(
        self,
        uri: str,
        *,
        method: str = METH_GET,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
    ) -> Any:
        """Handle a request to the Balena Cloud API.

        Args:
        ----
            uri: Request URI, without '/api/', for example, 'status'.
            method: HTTP method to use.
            params: Query parameters to include in the request.
            data: Data to include in the request.

        Returns:
        -------
            A Python dictionary (JSON decoded) with the response from
            the Balena Cloud API.

        Raises:
        ------
            BalenaCloudConnectionError: If a connection error occurs.
            BalenaCloudAuthenticationError: If the request is unauthorized.
            BalenaCloudError: If an unexpected error

        """
        url = URL.build(
            scheme="https",
            host="api.balena-cloud.com",
            path="/v7/",
        ).join(URL(uri))

        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.token}",
            "User-Agent": f"PythonBalenaCloud/{VERSION}",
        }

        if self.session is None:
            self.session = ClientSession()
            self._close_session = True

        try:
            async with asyncio.timeout(self.request_timeout):
                response = await self.session.request(
                    method,
                    url,
                    headers=headers,
                    params=params,
                    json=data,
                    ssl=True,
                )
                response.raise_for_status()
        except TimeoutError as exception:
            msg = "Timeout occurred while connecting to the Balena Cloud API."
            raise BalenaCloudConnectionError(msg) from exception
        except ClientResponseError as exception:
            if exception.status == 401:
                msg = "The request to the Balena Cloud API was unauthorized."
                raise BalenaCloudAuthenticationError(msg) from exception
            msg = "Error occurred while connecting to the Balena Cloud API."
            raise BalenaCloudConnectionError(msg) from exception
        except (ClientError, socket.gaierror) as exception:
            msg = "Error occurred while connecting to the Balena Cloud API."
            raise BalenaCloudConnectionError(msg) from exception

        if method not in {METH_DELETE, METH_PATCH}:
            content_type = response.headers.get("Content-Type", "")
            if "application/json" not in content_type:
                text = await response.text()
                msg = "Unexpected content type response from the Balena Cloud API."
                raise BalenaCloudError(
                    msg, {"Content-Type": content_type, "Response": text}
                )

            return await response.json()
        return None

    # Organizations
    async def get_organizations(self) -> list[Organization]:
        """Get all organizations that is authorized by the user.

        Returns
        -------
            A list of organizations.

        """
        response = await self._request("organization")
        return [Organization.from_dict(item) for item in response["d"]]

    async def get_organization(
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
            response = await self._request(f"organization({org_id})")
        else:
            response = await self._request(f"organization(handle='{org_handle}')")
        if not response["d"]:
            msg = "No organization found with the provided ID or handle."
            raise BalenaCloudResourceNotFoundError(msg)
        return Organization.from_dict(response["d"][0])

    # Fleets
    async def get_fleets(self) -> list[Fleet]:
        """Get all fleets that is authorized by the user.

        Returns
        -------
            A list of fleets.

        """
        response = await self._request(
            "application",
            params={"$filter": "is_directly_accessible_by__user/any(dau:true)"},
        )
        return [Fleet.from_dict(item) for item in response["d"]]

    async def get_fleet(
        self,
        fleet_id: int | None = None,
        fleet_slug: str | None = None,
        fleet_name: str | None = None,
    ) -> Fleet:
        """Get a fleet by its ID, slug or name.

        Args:
        ----
            fleet_id: The fleet ID (optional).
            fleet_slug: The fleet slug (optional).
            fleet_name: The fleet name (optional).

        Returns:
        -------
            A fleet object.

        """
        if fleet_id is None and fleet_slug is None and fleet_name is None:
            msg = "You must provide either a fleet ID, a fleet slug or a fleet name."
            raise BalenaCloudParameterValidationError(msg)

        if fleet_id is not None:
            response = await self._request(f"application({fleet_id})")
        elif fleet_slug is not None:
            response = await self._request(f"application(slug='{fleet_slug}')")
        else:
            response = await self._request(
                "application", params={"$filter": f"app_name eq '{fleet_name}'"}
            )
        if not response["d"]:
            msg = "No fleet found with the provided ID, slug or name."
            raise BalenaCloudResourceNotFoundError(msg)
        return Fleet.from_dict(response["d"][0])

    async def get_fleet_devices(self, fleet_id: int) -> list[Device]:
        """Get all devices from a specific fleet.

        Args:
        ----
            fleet_id: The fleet ID.

        Returns:
        -------
            A list of devices in the fleet.

        """
        response = await self._request(
            "device", params={"$filter": f"belongs_to__application eq '{fleet_id}'"}
        )
        return [Device.from_dict(item) for item in response["d"]]

    async def get_organization_fleets(self, org_handle: str) -> list[Fleet]:
        """Get all fleets from an organization.

        Args:
        ----
            org_handle: The organization handle.

        Returns:
        -------
            A list of organization fleets.

        """
        response = await self._request(
            "application",
            params={"$filter": f"organization/any(o:o/handle eq '{org_handle}')"},
        )
        return [Fleet.from_dict(item) for item in response["d"]]

    # Devices
    async def get_device(
        self,
        device_id: int | None = None,
        device_uuid: str | None = None,
    ) -> Device:
        """Get a device by its ID.

        Args:
        ----
            device_id: The device ID (optional).
            device_uuid: The device UUID (optional).

        Returns:
        -------
            A device object.

        """
        if device_id is None and device_uuid is None:
            msg = "You must provide either a device ID or a device UUID."
            raise BalenaCloudParameterValidationError(msg)

        if device_id is not None:
            response = await self._request(f"device({device_id})")
        else:
            response = await self._request(f"device(uuid='{device_uuid}')")
        if not response["d"]:
            msg = "No device found with the provided ID or UUID."
            raise BalenaCloudResourceNotFoundError(msg)
        return Device.from_dict(response["d"][0])

    async def update_device(
        self,
        device_id: int,
        data: dict[str, str],
    ) -> None:
        """Change a device with the provided data.

        Args:
        ----
            device_id: The device ID.
            data: The data to update the device.

        """
        await self._request(f"device({device_id})", method=METH_PATCH, data=data)

    async def remove_device(self, device_id: int) -> None:
        """Remove a device.

        Args:
        ----
            device_id: The device ID.

        """
        await self._request(f"device({device_id})", method=METH_DELETE)

    # Device - Tags
    async def get_device_tags(
        self,
        device_id: int | None = None,
        device_uuid: str | None = None,
    ) -> list[Tag]:
        """Get all tags from a device.

        Args:
        ----
            device_id: The device ID (optional).
            device_uuid: The device UUID (optional).

        Returns:
        -------
            A list of tags in the device.

        """
        if device_id is None and device_uuid is None:
            msg = "You must provide either a device ID or a device UUID."
            raise BalenaCloudParameterValidationError(msg)

        if device_id is not None:
            response = await self._request(
                "device_tag",
                params={"$filter": f"device eq {device_id}"},
            )
        else:
            response = await self._request(
                "device_tag",
                params={"$filter": f"device/uuid eq '{device_uuid}'"},
            )
        return [Tag.from_dict(item) for item in response["d"]]

    async def add_device_tag(
        self,
        device_id: int,
        key: str,
        value: str,
    ) -> Tag:
        """Add a new tag to a device.

        Args:
        ----
            device_id: The device ID.
            key: The tag key.
            value: The tag value.

        Returns:
        -------
            The tag object.

        """
        response = await self._request(
            "device_tag",
            method=METH_POST,
            data={"device": device_id, "tag_key": key, "value": value},
        )
        return Tag.from_dict(response)

    async def update_device_tag(
        self,
        device_id: int,
        key: str,
        value: str,
    ) -> None:
        """Update a tag from a device.

        Args:
        ----
            device_id: The device ID.
            key: The tag key.
            value: The new tag value.

        """
        await self._request(
            f"device_tag(device={device_id},tag_key='{key}')",
            method=METH_PATCH,
            data={"value": value},
        )

    async def remove_device_tag(self, tag_id: int) -> None:
        """Remove a tag from a device.

        Args:
        ----
            tag_id: The tag ID.

        """
        await self._request(
            f"device_tag({tag_id})",
            method=METH_DELETE,
        )

    # Device - Environment Variables
    async def get_device_variables(
        self,
        device_id: int | None = None,
        device_uuid: str | None = None,
    ) -> list[EnvironmentVariable]:
        """Get all environment variables from a device.

        Args:
        ----
            device_id: The device ID (optional).
            device_uuid: The device UUID (optional).

        Returns:
        -------
            A list of environment variables in the device.

        """
        if device_id is None and device_uuid is None:
            msg = "You must provide either a device ID or a device UUID."
            raise BalenaCloudParameterValidationError(msg)

        if device_id is not None:
            response = await self._request(
                "device_environment_variable",
                params={"$filter": f"device eq {device_id}"},
            )
        else:
            response = await self._request(
                "device_environment_variable",
                params={"$filter": f"device/any(d:d/uuid eq '{device_uuid}')"},
            )
        return [EnvironmentVariable.from_dict(item) for item in response["d"]]

    async def add_device_variable(
        self,
        device_id: int,
        name: str,
        value: str,
    ) -> EnvironmentVariable:
        """Add a new environment variable to a device.

        Args:
        ----
            device_id: The device ID.
            name: The variable name.
            value: The variable value.

        """
        response = await self._request(
            "device_environment_variable",
            method=METH_POST,
            data={"device": device_id, "name": name, "value": value},
        )
        return EnvironmentVariable.from_dict(response)

    async def update_device_variable(self, variable_id: int, value: str) -> None:
        """Update an environment variable from a device.

        Args:
        ----
            variable_id: The variable ID.
            value: The new variable value.

        """
        await self._request(
            f"device_environment_variable({variable_id})",
            method=METH_PATCH,
            data={"value": value},
        )

    async def remove_device_variable(self, variable_id: int) -> None:
        """Remove an environment variable from a device.

        Args:
        ----
            variable_id: The variable ID.

        """
        await self._request(
            f"device_environment_variable({variable_id})",
            method=METH_DELETE,
        )

    async def close(self) -> None:
        """Close open client session."""
        if self.session and self._close_session:
            await self.session.close()

    async def __aenter__(self) -> Self:
        """Async enter.

        Returns
        -------
            The Balena Cloud object.

        """
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        """Async exit.

        Args:
        ----
            _exc_info: Exec type.

        """
        await self.close()