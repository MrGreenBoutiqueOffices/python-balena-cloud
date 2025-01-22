"""Test the devices model for Balena Cloud."""

# pylint: disable=too-many-arguments,too-many-positional-arguments
from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest
from aresponses import ResponsesMockServer
from syrupy.assertion import SnapshotAssertion

from . import load_fixtures

if TYPE_CHECKING:
    from balena_cloud import BalenaCloud


@pytest.mark.parametrize(
    ("param_key", "param_value", "endpoint"),
    [
        ("device_id", 1, "/v7/device(1)"),
        ("device_uuid", "test-uuid", "/v7/device(uuid='test-uuid')"),
    ],
)
async def test_get_device(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    balena_cloud_client: BalenaCloud,
    param_key: str,
    param_value: Any,
    endpoint: str,
) -> None:
    """Test the get_device method."""
    aresponses.add(
        "api.balena-cloud.com",
        endpoint,
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("devices/device.json"),
        ),
    )
    # Get the device based on the parameter key
    device = None
    if param_key == "device_id":
        device = await balena_cloud_client.device.get(device_id=param_value)
    elif param_key == "device_uuid":
        device = await balena_cloud_client.device.get(device_uuid=param_value)
    assert device == snapshot


async def test_update_device(
    aresponses: ResponsesMockServer,
    balena_cloud_client: BalenaCloud,
) -> None:
    """Test the update_device method."""
    aresponses.add(
        "api.balena-cloud.com",
        "/v7/device(1)",
        "PATCH",
    )
    await balena_cloud_client.device.update(
        device_id=1, data={"device_name": "Test Device"}
    )


async def test_remove_device(
    aresponses: ResponsesMockServer,
    balena_cloud_client: BalenaCloud,
) -> None:
    """Test the remove_device method."""
    aresponses.add(
        "api.balena-cloud.com",
        "/v7/device(1)",
        "DELETE",
    )
    await balena_cloud_client.device.remove(device_id=1)


@pytest.mark.parametrize(
    ("param_key", "param_value"),
    [
        ("device_id", 1),
        ("device_uuid", "test-uuid"),
    ],
)
async def test_get_device_tags(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    balena_cloud_client: BalenaCloud,
    param_key: str,
    param_value: Any,
) -> None:
    """Test the get_device_tags method."""
    aresponses.add(
        "api.balena-cloud.com",
        "/v7/device_tag",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("devices/device_tags.json"),
        ),
    )
    # Get the device tags based on the parameter key
    tags = None
    if param_key == "device_id":
        tags = await balena_cloud_client.device_tag.get_all(device_id=param_value)
    elif param_key == "device_uuid":
        tags = await balena_cloud_client.device_tag.get_all(device_uuid=param_value)
    assert tags == snapshot


async def test_add_device_tag(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    balena_cloud_client: BalenaCloud,
) -> None:
    """Test the add_device_tag method."""
    aresponses.add(
        "api.balena-cloud.com",
        "/v7/device_tag",
        "POST",
        aresponses.Response(
            status=201,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("devices/post_device_tag.json"),
        ),
    )
    tag = await balena_cloud_client.device_tag.add(
        device_id=1, key="test_key", value="test_value"
    )
    assert tag == snapshot


async def test_update_device_tag(
    aresponses: ResponsesMockServer,
    balena_cloud_client: BalenaCloud,
) -> None:
    """Test the update_device_tag method."""
    aresponses.add(
        "api.balena-cloud.com",
        "/v7/device_tag(device=1,tag_key='test_key')",
        "PATCH",
    )
    await balena_cloud_client.device_tag.update(
        device_id=1, key="test_key", value="test_value"
    )


async def test_remove_device_tag(
    aresponses: ResponsesMockServer,
    balena_cloud_client: BalenaCloud,
) -> None:
    """Test the remove_device_tag method."""
    aresponses.add(
        "api.balena-cloud.com",
        "/v7/device_tag(1)",
        "DELETE",
    )
    await balena_cloud_client.device_tag.remove(tag_id=1)


@pytest.mark.parametrize(
    ("param_key", "param_value"),
    [
        ("device_id", 1),
        ("device_uuid", "test-uuid"),
    ],
)
async def test_get_device_variables(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    balena_cloud_client: BalenaCloud,
    param_key: str,
    param_value: Any,
) -> None:
    """Test the get_device_variables method."""
    aresponses.add(
        "api.balena-cloud.com",
        "/v7/device_environment_variable",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("devices/device_variables.json"),
        ),
    )
    # Get the device variables based on the parameter key
    variables = None
    if param_key == "device_id":
        variables = await balena_cloud_client.device_variable.get_all(
            device_id=param_value
        )
    elif param_key == "device_uuid":
        variables = await balena_cloud_client.device_variable.get_all(
            device_uuid=param_value
        )
    assert variables == snapshot


async def test_add_device_variable(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    balena_cloud_client: BalenaCloud,
) -> None:
    """Test the add_device_variable method."""
    aresponses.add(
        "api.balena-cloud.com",
        "/v7/device_environment_variable",
        "POST",
        aresponses.Response(
            status=201,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("devices/post_device_variable.json"),
        ),
    )
    variable = await balena_cloud_client.device_variable.add(
        device_id=1, name="test_name", value="test_value"
    )
    assert variable == snapshot


async def test_update_device_variable(
    aresponses: ResponsesMockServer,
    balena_cloud_client: BalenaCloud,
) -> None:
    """Test the update_device_variable method."""
    aresponses.add(
        "api.balena-cloud.com",
        "/v7/device_environment_variable(1)",
        "PATCH",
    )
    await balena_cloud_client.device_variable.update(variable_id=1, value="test_value")


async def test_remove_device_variable(
    aresponses: ResponsesMockServer,
    balena_cloud_client: BalenaCloud,
) -> None:
    """Test the remove_device_variable method."""
    aresponses.add(
        "api.balena-cloud.com",
        "/v7/device_environment_variable(1)",
        "DELETE",
    )
    await balena_cloud_client.device_variable.remove(variable_id=1)
