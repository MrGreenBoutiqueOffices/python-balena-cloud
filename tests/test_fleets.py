"""Test the fleets model for Balena Cloud."""

# pylint: disable=too-many-arguments,too-many-positional-arguments
from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest
from aresponses import ResponsesMockServer
from syrupy.assertion import SnapshotAssertion

from . import load_fixtures

if TYPE_CHECKING:
    from balena_cloud import BalenaCloud


async def test_get_fleets(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    balena_cloud_client: BalenaCloud,
) -> None:
    """Test the get_fleets method."""
    aresponses.add(
        "api.balena-cloud.com",
        "/v7/application",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("fleets/all_fleets.json"),
        ),
    )
    fleets = await balena_cloud_client.fleet.get_all()
    assert fleets == snapshot


@pytest.mark.parametrize(
    ("param_key", "param_value", "endpoint"),
    [
        ("fleet_id", 1, "/v7/application(1)"),
        ("fleet_slug", "test-slug", "/v7/application(slug='test-slug')"),
        ("fleet_name", "Test Fleet", "/v7/application"),
    ],
)
async def test_get_fleet(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    balena_cloud_client: BalenaCloud,
    param_key: str,
    param_value: Any,
    endpoint: str,
) -> None:
    """Test the get_fleet method."""
    aresponses.add(
        "api.balena-cloud.com",
        endpoint,
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("fleets/fleet.json"),
        ),
    )
    # Get the fleet based on the parameter key
    fleet = None
    if param_key == "fleet_id":
        fleet = await balena_cloud_client.fleet.get(fleet_id=param_value)
    elif param_key == "fleet_slug":
        fleet = await balena_cloud_client.fleet.get(fleet_slug=param_value)
    elif param_key == "fleet_name":
        fleet = await balena_cloud_client.fleet.get(fleet_name=param_value)
    assert fleet == snapshot


async def test_get_fleet_devices(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    balena_cloud_client: BalenaCloud,
) -> None:
    """Test the get_fleet_devices method."""
    aresponses.add(
        "api.balena-cloud.com",
        "/v7/device",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("fleets/fleet_devices.json"),
        ),
    )
    devices = await balena_cloud_client.fleet.get_devices(fleet_id=1)
    assert devices == snapshot


async def test_get_filtered_fleet_devices(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    balena_cloud_client: BalenaCloud,
) -> None:
    """Test the get_fleet_devices method with filters."""
    aresponses.add(
        "api.balena-cloud.com",
        "/v7/device",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("fleets/fleet_devices.json"),
        ),
    )
    devices = await balena_cloud_client.fleet.get_devices(
        fleet_id=1, filters={"is_online": True}
    )
    assert devices == snapshot


async def test_get_organization_fleets(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    balena_cloud_client: BalenaCloud,
) -> None:
    """Test the get_organization_fleets method."""
    aresponses.add(
        "api.balena-cloud.com",
        "/v7/application",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("fleets/all_fleets.json"),
        ),
    )
    fleets = await balena_cloud_client.organization.get_fleets(org_handle="test-org")
    assert fleets == snapshot


async def test_get_fleet_releases(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    balena_cloud_client: BalenaCloud,
) -> None:
    """Test the get_fleet_releases method."""
    aresponses.add(
        "api.balena-cloud.com",
        "/v7/release",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("fleets/fleet_releases.json"),
        ),
    )
    releases = await balena_cloud_client.fleet.get_releases(fleet_id=1)
    assert releases == snapshot


async def test_get_filtered_fleet_releases(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    balena_cloud_client: BalenaCloud,
) -> None:
    """Test the get_fleet_releases method with filters."""
    aresponses.add(
        "api.balena-cloud.com",
        "/v7/release",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("fleets/fleet_releases.json"),
        ),
    )
    releases = await balena_cloud_client.fleet.get_releases(
        fleet_id=1, filters={"is_final": True}
    )
    assert releases == snapshot


async def test_get_fleet_service_variable(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    balena_cloud_client: BalenaCloud,
) -> None:
    """Test the get_fleet_service_variable method."""
    aresponses.add(
        "api.balena-cloud.com",
        "/v7/service_environment_variable(1)",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("fleets/fleet_service_variable.json"),
        ),
    )
    variable = await balena_cloud_client.fleet_service_variable.get(variable_id=1)
    assert variable == snapshot


async def test_get_fleet_service_variables(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    balena_cloud_client: BalenaCloud,
) -> None:
    """Test the get_fleet_service_variables method."""
    aresponses.add(
        "api.balena-cloud.com",
        "/v7/service_environment_variable",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("fleets/fleet_service_variables.json"),
        ),
    )
    variables = await balena_cloud_client.fleet_service_variable.get_all(service_id=1)
    assert variables == snapshot


async def test_add_fleet_service_variable(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    balena_cloud_client: BalenaCloud,
) -> None:
    """Test the add_fleet_service_variable method."""
    aresponses.add(
        "api.balena-cloud.com",
        "/v7/service_environment_variable",
        "POST",
        aresponses.Response(
            status=201,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("fleets/post_fleet_service_variable.json"),
        ),
    )
    variable = await balena_cloud_client.fleet_service_variable.add(
        service_id=1, name="test_name", value="test_value"
    )
    assert variable == snapshot


async def test_update_fleet_service_variable(
    aresponses: ResponsesMockServer,
    balena_cloud_client: BalenaCloud,
) -> None:
    """Test the update_fleet_service_variable method."""
    aresponses.add(
        "api.balena-cloud.com",
        "/v7/service_environment_variable(1)",
        "PATCH",
    )
    await balena_cloud_client.fleet_service_variable.update(
        variable_id=1, value="test_value"
    )


async def test_update_fleet_service_variable_numeric_value(
    aresponses: ResponsesMockServer,
    balena_cloud_client: BalenaCloud,
) -> None:
    """Test the update_fleet_service_variable method with a numeric value."""
    aresponses.add(
        "api.balena-cloud.com",
        "/v7/service_environment_variable(1)",
        "PATCH",
    )
    await balena_cloud_client.fleet_service_variable.update(
        variable_id=1, value=1414930252
    )


async def test_remove_fleet_service_variable(
    aresponses: ResponsesMockServer,
    balena_cloud_client: BalenaCloud,
) -> None:
    """Test the remove_fleet_service_variable method."""
    aresponses.add(
        "api.balena-cloud.com",
        "/v7/service_environment_variable(1)",
        "DELETE",
    )
    await balena_cloud_client.fleet_service_variable.remove(variable_id=1)
