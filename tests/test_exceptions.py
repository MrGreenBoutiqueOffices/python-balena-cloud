"""Test exceptions for Balena Cloud."""

# pylint: disable=protected-access
# pylint: disable=too-many-arguments,too-many-positional-arguments
from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from aresponses import ResponsesMockServer

from balena_cloud.exceptions import (
    BalenaCloudAuthenticationError,
    BalenaCloudConnectionError,
    BalenaCloudError,
    BalenaCloudParameterValidationError,
    BalenaCloudResourceNotFoundError,
)

from . import load_fixtures

if TYPE_CHECKING:
    from balena_cloud import BalenaCloud


async def test_client_response_error(
    aresponses: ResponsesMockServer, balena_cloud_client: BalenaCloud
) -> None:
    """Test the client response error."""
    aresponses.add(
        "api.balena-cloud.com",
        "/v7/test",
        "GET",
        aresponses.Response(
            status=404,
            headers={"Content-Type": "application/json"},
        ),
    )
    with pytest.raises(BalenaCloudConnectionError):
        await balena_cloud_client.request("test")


async def test_unauthorized_error(
    aresponses: ResponsesMockServer, balena_cloud_client: BalenaCloud
) -> None:
    """Test the unauthorized exception."""
    aresponses.add(
        "api.balena-cloud.com",
        "/v7/test",
        "GET",
        aresponses.Response(
            status=401,
            headers={"Content-Type": "application/json"},
        ),
    )
    with pytest.raises(BalenaCloudAuthenticationError):
        await balena_cloud_client.request("test")


@pytest.mark.parametrize(
    ("endpoint", "namespace", "method", "exception"),
    [
        (
            "/v7/organization",
            "organization",
            "get",
            BalenaCloudParameterValidationError,
        ),
        ("/v7/application", "fleet", "get", BalenaCloudParameterValidationError),
        ("/v7/device", "device", "get", BalenaCloudParameterValidationError),
        (
            "/v7/device_tag",
            "device_tag",
            "get_all",
            BalenaCloudParameterValidationError,
        ),
        (
            "/v7/device_variable",
            "device_variable",
            "get_all",
            BalenaCloudParameterValidationError,
        ),
    ],
)
async def test_resource_parameter_error(
    aresponses: ResponsesMockServer,
    balena_cloud_client: BalenaCloud,
    endpoint: str,
    namespace: str,
    method: str,
    exception: type[BalenaCloudError],
) -> None:
    """Test the organization parameter error."""
    aresponses.add(
        "api.balena-cloud.com",
        endpoint,
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
        ),
    )
    client = getattr(balena_cloud_client, namespace)
    method_to_call = getattr(client, method)

    with pytest.raises(exception):
        await method_to_call()


@pytest.mark.parametrize(
    ("endpoint", "namespace", "exception", "params"),
    [
        (
            "/v7/organization(1)",
            "organization",
            BalenaCloudResourceNotFoundError,
            {"org_id": 1},
        ),
        (
            "/v7/application(1)",
            "fleet",
            BalenaCloudResourceNotFoundError,
            {"fleet_id": 1},
        ),
        (
            "/v7/device(1)",
            "device",
            BalenaCloudResourceNotFoundError,
            {"device_id": 1},
        ),
        (
            "/v7/release(1)",
            "release",
            BalenaCloudResourceNotFoundError,
            {"release_id": 1},
        ),
    ],
)
async def test_resource_not_found_error(
    aresponses: ResponsesMockServer,
    balena_cloud_client: BalenaCloud,
    endpoint: str,
    namespace: str,
    exception: type[BalenaCloudError],
    params: dict[str, int],
) -> None:
    """Test resource not found errors."""
    aresponses.add(
        "api.balena-cloud.com",
        endpoint,
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("no_data.json"),
        ),
    )
    with pytest.raises(exception):
        await getattr(balena_cloud_client, namespace).get(**params)
