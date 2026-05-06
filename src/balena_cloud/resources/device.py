"""Device resource clients."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aiohttp.hdrs import METH_DELETE, METH_PATCH, METH_POST

from balena_cloud.exceptions import (
    BalenaCloudParameterValidationError,
    BalenaCloudResourceNotFoundError,
)
from balena_cloud.models import Device, EnvironmentVariable, Tag


@dataclass
class DeviceResource:
    """Resource client for device related requests."""

    parent: Any

    async def get(
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
            response = await self.parent.request(f"device({device_id})")
        else:
            response = await self.parent.request(f"device(uuid='{device_uuid}')")
        if not response["d"]:
            msg = "No device found with the provided ID or UUID."
            raise BalenaCloudResourceNotFoundError(msg)
        return Device.from_dict(response["d"][0])

    async def update(
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
        await self.parent.request(f"device({device_id})", method=METH_PATCH, data=data)

    async def remove(self, device_id: int) -> None:
        """Remove a device.

        Args:
        ----
            device_id: The device ID.

        """
        await self.parent.request(f"device({device_id})", method=METH_DELETE)


@dataclass
class DeviceTagResource:
    """Resource client for device tag related requests."""

    parent: Any

    async def get(self, tag_id: int) -> Tag:
        """Get a device tag by its ID.

        Args:
        ----
            tag_id: The tag ID.

        Returns:
        -------
            A tag object.

        """
        response = await self.parent.request(f"device_tag({tag_id})")
        if not response["d"]:
            msg = "No device tag found with the provided ID."
            raise BalenaCloudResourceNotFoundError(msg)
        return Tag.from_dict(response["d"][0])

    async def get_all(
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
            response = await self.parent.request(
                "device_tag",
                params={"$filter": f"device eq {device_id}"},
            )
        else:
            response = await self.parent.request(
                "device_tag",
                params={"$filter": f"device/uuid eq '{device_uuid}'"},
            )
        return [Tag.from_dict(item) for item in response["d"]]

    async def add(
        self,
        device_id: int,
        key: str,
        value: object,
    ) -> Tag:
        """Add a new tag to a device.

        Args:
        ----
            device_id: The device ID.
            key: The tag key.
            value (String): The tag value.

        Returns:
        -------
            The tag object.

        """
        response = await self.parent.request(
            "device_tag",
            method=METH_POST,
            data={"device": device_id, "tag_key": key, "value": str(value)},
        )
        return Tag.from_dict(response)

    async def update(
        self,
        device_id: int,
        key: str,
        value: object,
    ) -> None:
        """Update a tag from a device.

        Args:
        ----
            device_id: The device ID.
            key: The tag key.
            value: The new tag value.

        """
        await self.parent.request(
            f"device_tag(device={device_id},tag_key='{key}')",
            method=METH_PATCH,
            data={"value": str(value)},
        )

    async def remove(self, tag_id: int) -> None:
        """Remove a tag from a device.

        Args:
        ----
            tag_id: The tag ID.

        """
        await self.parent.request(
            f"device_tag({tag_id})",
            method=METH_DELETE,
        )


@dataclass
class DeviceVariableResource:
    """Resource client for device variable related requests."""

    parent: Any

    async def get(self, variable_id: int) -> EnvironmentVariable:
        """Get an environment variable by its ID from device.

        Args:
        ----
            variable_id: The variable ID.

        Returns:
        -------
            An environment variable object.

        """
        response = await self.parent.request(
            f"device_environment_variable({variable_id})"
        )
        if not response["d"]:
            msg = "No device environment variable found with the provided ID."
            raise BalenaCloudResourceNotFoundError(msg)
        return EnvironmentVariable.from_dict(response["d"][0])

    async def get_all(
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
            response = await self.parent.request(
                "device_environment_variable",
                params={"$filter": f"device eq {device_id}"},
            )
        else:
            response = await self.parent.request(
                "device_environment_variable",
                params={"$filter": f"device/any(d:d/uuid eq '{device_uuid}')"},
            )
        return [EnvironmentVariable.from_dict(item) for item in response["d"]]

    async def add(
        self,
        device_id: int,
        name: str,
        value: object,
    ) -> EnvironmentVariable:
        """Add a new environment variable to a device.

        Args:
        ----
            device_id: The device ID.
            name: The variable name.
            value (String): The variable value.

        """
        response = await self.parent.request(
            "device_environment_variable",
            method=METH_POST,
            data={"device": device_id, "name": name, "value": str(value)},
        )
        return EnvironmentVariable.from_dict(response)

    async def update(self, variable_id: int, value: object) -> None:
        """Update an environment variable from a device.

        Args:
        ----
            variable_id: The variable ID.
            value: The new variable value.

        """
        await self.parent.request(
            f"device_environment_variable({variable_id})",
            method=METH_PATCH,
            data={"value": str(value)},
        )

    async def remove(self, variable_id: int) -> None:
        """Remove an environment variable from a device.

        Args:
        ----
            variable_id: The variable ID.

        """
        await self.parent.request(
            f"device_environment_variable({variable_id})",
            method=METH_DELETE,
        )


@dataclass
class DeviceServiceVariableResource:
    """Resource client for device service variable related requests."""

    parent: Any

    async def get(self, variable_id: int) -> EnvironmentVariable:
        """Get a service environment variable by its ID from a device.

        Args:
        ----
            variable_id: The variable ID.

        Returns:
        -------
            An environment variable object.

        """
        response = await self.parent.request(
            f"device_service_environment_variable({variable_id})"
        )
        if not response["d"]:
            msg = "No device service environment variable found with the provided ID."
            raise BalenaCloudResourceNotFoundError(msg)
        return EnvironmentVariable.from_dict(response["d"][0])

    async def get_all(
        self,
        device_id: int | None = None,
        device_uuid: str | None = None,
    ) -> list[EnvironmentVariable]:
        """Get all service environment variables from a device.

        Args:
        ----
            device_id: The device ID (optional).
            device_uuid: The device UUID (optional).

        Returns:
        -------
            A list of service environment variables in the device.

        """
        if device_id is None and device_uuid is None:
            msg = "You must provide either a device ID or a device UUID."
            raise BalenaCloudParameterValidationError(msg)

        if device_id is not None:
            response = await self.parent.request(
                "device_service_environment_variable",
                params={"$filter": f"service_install/device eq {device_id}"},
            )
        else:
            response = await self.parent.request(
                "device_service_environment_variable",
                params={
                    "$filter": (
                        "service_install/any(si:si/device/any("
                        f"d:d/uuid eq '{device_uuid}'))"
                    )
                },
            )
        return [EnvironmentVariable.from_dict(item) for item in response["d"]]

    async def add(
        self,
        service_install_id: int,
        name: str,
        value: object,
    ) -> EnvironmentVariable:
        """Add a new service environment variable to a device.

        Args:
        ----
            service_install_id: The service install ID.
            name: The variable name.
            value (String): The variable value.

        """
        response = await self.parent.request(
            "device_service_environment_variable",
            method=METH_POST,
            data={
                "service_install": service_install_id,
                "name": name,
                "value": str(value),
            },
        )
        return EnvironmentVariable.from_dict(response)

    async def update(self, variable_id: int, value: object) -> None:
        """Update a service environment variable from a device.

        Args:
        ----
            variable_id: The variable ID.
            value: The new variable value.

        """
        await self.parent.request(
            f"device_service_environment_variable({variable_id})",
            method=METH_PATCH,
            data={"value": str(value)},
        )

    async def remove(self, variable_id: int) -> None:
        """Remove a service environment variable from a device.

        Args:
        ----
            variable_id: The variable ID.

        """
        await self.parent.request(
            f"device_service_environment_variable({variable_id})",
            method=METH_DELETE,
        )
