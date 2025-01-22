"""Test the releases model for Balena Cloud."""

# pylint: disable=too-many-arguments,too-many-positional-arguments
from __future__ import annotations

from typing import TYPE_CHECKING

from aresponses import ResponsesMockServer
from syrupy.assertion import SnapshotAssertion

from . import load_fixtures

if TYPE_CHECKING:
    from balena_cloud import BalenaCloud


async def test_get_release(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    balena_cloud_client: BalenaCloud,
) -> None:
    """Test the get_release method."""
    aresponses.add(
        "api.balena-cloud.com",
        "/v7/release(1)",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("releases/release.json"),
        ),
    )
    release = await balena_cloud_client.get_release(release_id=1)
    assert release == snapshot


async def test_remove_release(
    aresponses: ResponsesMockServer,
    balena_cloud_client: BalenaCloud,
) -> None:
    """Test the remove_release method."""
    aresponses.add(
        "api.balena-cloud.com",
        "/v7/release(1)",
        "DELETE",
    )
    await balena_cloud_client.remove_release(release_id=1)
