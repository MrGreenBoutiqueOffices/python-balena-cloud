"""Fleet resource clients."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aiohttp.hdrs import METH_DELETE, METH_PATCH, METH_POST

from balena_cloud.exceptions import (
    BalenaCloudParameterValidationError,
    BalenaCloudResourceNotFoundError,
)
from balena_cloud.models import Device, EnvironmentVariable, Fleet, Release, Service


@dataclass
class FleetResource:
    """Resource client for fleet related requests."""

    parent: Any

    async def get_all(self) -> list[Fleet]:
        """Get all fleets that is authorized by the user.

        Returns
        -------
            A list of fleets.

        """
        response = await self.parent.request(
            "application",
            params={"$filter": "is_directly_accessible_by__user/any(dau:true)"},
        )
        return [Fleet.from_dict(item) for item in response["d"]]

    async def get(
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
            response = await self.parent.request(f"application({fleet_id})")
        elif fleet_slug is not None:
            response = await self.parent.request(f"application(slug='{fleet_slug}')")
        else:
            response = await self.parent.request(
                "application", params={"$filter": f"app_name eq '{fleet_name}'"}
            )
        if not response["d"]:
            msg = "No fleet found with the provided ID, slug or name."
            raise BalenaCloudResourceNotFoundError(msg)
        return Fleet.from_dict(response["d"][0])

    async def get_devices(
        self,
        fleet_id: int,
        filters: dict[str, Any] | None = None,
    ) -> list[Device]:
        """Get all devices from a specific fleet.

        Args:
        ----
            fleet_id: The fleet ID.
            filters: Filters to apply to the request (optional).

        Returns:
        -------
            A list of devices in the fleet with the applied filters (if any).

        """
        if filters is None:
            response = await self.parent.request(
                "device",
                params={"$filter": f"belongs_to__application eq {fleet_id}"},
            )
        else:
            query = f"belongs_to__application eq {fleet_id}"
            for key, value in filters.items():
                query += f" and {key} eq '{value}'"
            response = await self.parent.request("device", params={"$filter": query})
        return [Device.from_dict(item) for item in response["d"]]

    async def get_releases(
        self,
        fleet_id: int,
        filters: dict[str, Any] | None = None,
    ) -> list[Release]:
        """Get all releases from a specific fleet.

        Args:
        ----
            fleet_id: The fleet ID.
            filters: Filters to apply to the request (optional).

        Returns:
        -------
            A list of releases in the fleet with the applied filters (if any).

        """
        if filters is None:
            response = await self.parent.request(
                "release",
                params={"$filter": f"belongs_to__application eq {fleet_id}"},
            )
        else:
            query = f"belongs_to__application eq {fleet_id}"
            for key, value in filters.items():
                query += f" and {key} eq '{value}'"
            response = await self.parent.request("release", params={"$filter": query})
        return [Release.from_dict(item) for item in response["d"]]

    async def get_services(
        self,
        fleet_id: int,
        filters: dict[str, Any] | None = None,
    ) -> list[Service]:
        """Get all services from a specific fleet.

        Args:
        ----
            fleet_id: The fleet ID.
            filters: Filters to apply to the request (optional).

        Returns:
        -------
            A list of services in the fleet with the applied filters (if any).

        """
        if filters is None:
            response = await self.parent.request(
                "service",
                params={"$filter": f"application eq {fleet_id}"},
            )
        else:
            query = f"application eq {fleet_id}"
            for key, value in filters.items():
                query += f" and {key} eq '{value}'"
            response = await self.parent.request("service", params={"$filter": query})
        return [Service.from_dict(item) for item in response["d"]]


@dataclass
class ServiceResource:
    """Resource client for service related requests."""

    parent: Any

    async def get(self, service_id: int) -> Service:
        """Get a service by its ID.

        Args:
        ----
            service_id: The service ID.

        Returns:
        -------
            A service object.

        """
        response = await self.parent.request(f"service({service_id})")
        if not response["d"]:
            msg = "No service found with the provided ID."
            raise BalenaCloudResourceNotFoundError(msg)
        return Service.from_dict(response["d"][0])

    async def get_all(
        self,
        fleet_id: int | None = None,
        fleet_name: str | None = None,
        fleet_slug: str | None = None,
    ) -> list[Service]:
        """Get all services from a fleet.

        Args:
        ----
            fleet_id: The fleet ID (optional).
            fleet_name: The fleet name (optional).
            fleet_slug: The fleet slug (optional).

        Returns:
        -------
            A list of services in the fleet.

        """
        if fleet_id is None and fleet_name is None and fleet_slug is None:
            msg = "You must provide either a fleet ID, a fleet name or a fleet slug."
            raise BalenaCloudParameterValidationError(msg)

        if fleet_id is not None:
            filter_query = f"application eq {fleet_id}"
        elif fleet_name is not None:
            filter_query = f"application/app_name eq '{fleet_name}'"
        else:
            filter_query = f"application/slug eq '{fleet_slug}'"

        response = await self.parent.request(
            "service",
            params={"$filter": filter_query},
        )
        return [Service.from_dict(item) for item in response["d"]]


@dataclass
class FleetServiceVariableResource:
    """Resource client for fleet service variable related requests."""

    parent: Any

    async def get(self, variable_id: int) -> EnvironmentVariable:
        """Get a service environment variable by its ID from a fleet.

        Args:
        ----
            variable_id: The variable ID.

        Returns:
        -------
            An environment variable object.

        """
        response = await self.parent.request(
            f"service_environment_variable({variable_id})"
        )
        if not response["d"]:
            msg = "No fleet service environment variable found with the provided ID."
            raise BalenaCloudResourceNotFoundError(msg)
        return EnvironmentVariable.from_dict(response["d"][0])

    async def get_all(
        self,
        service_id: int | None = None,
    ) -> list[EnvironmentVariable]:
        """Get all service environment variables from a fleet service.

        Args:
        ----
            service_id: The service ID.

        Returns:
        -------
            A list of service environment variables in the fleet service.

        """
        if service_id is None:
            msg = "You must provide a service ID."
            raise BalenaCloudParameterValidationError(msg)

        response = await self.parent.request(
            "service_environment_variable",
            params={"$filter": f"service eq {service_id}"},
        )
        return [EnvironmentVariable.from_dict(item) for item in response["d"]]

    async def add(
        self,
        service_id: int,
        name: str,
        value: object,
    ) -> EnvironmentVariable:
        """Add a new service environment variable to a fleet.

        Args:
        ----
            service_id: The service ID.
            name: The variable name.
            value (String): The variable value.

        """
        response = await self.parent.request(
            "service_environment_variable",
            method=METH_POST,
            data={"service": service_id, "name": name, "value": str(value)},
        )
        return EnvironmentVariable.from_dict(response)

    async def update(self, variable_id: int, value: object) -> None:
        """Update a service environment variable from a fleet.

        Args:
        ----
            variable_id: The variable ID.
            value: The new variable value.

        """
        await self.parent.request(
            f"service_environment_variable({variable_id})",
            method=METH_PATCH,
            data={"value": str(value)},
        )

    async def remove(self, variable_id: int) -> None:
        """Remove a service environment variable from a fleet.

        Args:
        ----
            variable_id: The variable ID.

        """
        await self.parent.request(
            f"service_environment_variable({variable_id})",
            method=METH_DELETE,
        )
