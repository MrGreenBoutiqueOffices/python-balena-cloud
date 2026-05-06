"""Asynchronous Python client for Balena Cloud."""

from __future__ import annotations

import asyncio
import socket
from dataclasses import dataclass
from importlib import metadata
from typing import Any, Self

from aiohttp import ClientError, ClientResponseError, ClientSession
from aiohttp.hdrs import METH_DELETE, METH_GET, METH_PATCH
from yarl import URL

from .exceptions import (
    BalenaCloudAuthenticationError,
    BalenaCloudConflictError,
    BalenaCloudConnectionError,
    BalenaCloudError,
)
from .resources import (
    DeviceResource,
    DeviceServiceVariableResource,
    DeviceTagResource,
    DeviceVariableResource,
    FleetResource,
    FleetServiceVariableResource,
    OrganizationResource,
    ReleaseResource,
    ServiceResource,
)

VERSION: str = metadata.version(__package__)  # ty:ignore[invalid-argument-type]


@dataclass
class BalenaCloud:
    """Main class for handling connections with the Balena Cloud API."""

    token: str

    request_timeout: float = 10.0
    session: ClientSession | None = None

    _close_session: bool = False

    async def request(
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

                if response.status == 409:
                    response_data = await response.json()
                    raise BalenaCloudConflictError(response_data, response.status)

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

    def __post_init__(self) -> None:
        """Post resource client initialization."""
        self.organization = OrganizationResource(parent=self)
        self.fleet = FleetResource(parent=self)
        self.release = ReleaseResource(parent=self)
        self.service = ServiceResource(parent=self)
        self.device = DeviceResource(parent=self)
        self.device_tag = DeviceTagResource(parent=self)
        self.device_variable = DeviceVariableResource(parent=self)
        self.device_service_variable = DeviceServiceVariableResource(parent=self)
        self.fleet_service_variable = FleetServiceVariableResource(parent=self)

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
