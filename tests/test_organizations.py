"""Test the organizations model for Balena Cloud."""

# pylint: disable=too-many-arguments,too-many-positional-arguments
from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest
from aresponses import ResponsesMockServer
from syrupy.assertion import SnapshotAssertion

from . import load_fixtures

if TYPE_CHECKING:
    from balena_cloud import BalenaCloud


async def test_get_organizations(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    balena_cloud_client: BalenaCloud,
) -> None:
    """Test the get_organizations method."""
    aresponses.add(
        "api.balena-cloud.com",
        "/v7/organization",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("organizations/all_organizations.json"),
        ),
    )
    organizations = await balena_cloud_client.get_organizations()
    assert organizations == snapshot


@pytest.mark.parametrize(
    ("param_key", "param_value", "endpoint"),
    [
        ("org_id", 1, "/v7/organization(1)"),
        ("org_handle", "test-handle", "/v7/organization(handle='test-handle')"),
    ],
)
async def test_get_organization(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    balena_cloud_client: BalenaCloud,
    param_key: str,
    param_value: Any,
    endpoint: str,
) -> None:
    """Test the get_organization method."""
    aresponses.add(
        "api.balena-cloud.com",
        endpoint,
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("organizations/organization.json"),
        ),
    )
    # Get the organization based on the parameter key
    organization = None
    if param_key == "org_id":
        organization = await balena_cloud_client.get_organization(org_id=param_value)
    elif param_key == "org_handle":
        organization = await balena_cloud_client.get_organization(
            org_handle=param_value
        )
    assert organization == snapshot
