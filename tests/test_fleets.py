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
    fleets = await balena_cloud_client.get_fleets()
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
        fleet = await balena_cloud_client.get_fleet(fleet_id=param_value)
    elif param_key == "fleet_slug":
        fleet = await balena_cloud_client.get_fleet(fleet_slug=param_value)
    elif param_key == "fleet_name":
        fleet = await balena_cloud_client.get_fleet(fleet_name=param_value)
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
    devices = await balena_cloud_client.get_fleet_devices(fleet_id=1)
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
    fleets = await balena_cloud_client.get_organization_fleets(org_handle="test-org")
    assert fleets == snapshot
