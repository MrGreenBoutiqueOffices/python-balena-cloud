"""Basic tests for Balena Cloud."""

# pylint: disable=protected-access
import asyncio
from unittest.mock import patch

import pytest
from aiohttp import ClientError, ClientResponse, ClientSession
from aresponses import Response, ResponsesMockServer

from balena_cloud import BalenaCloud
from balena_cloud.exceptions import BalenaCloudConnectionError, BalenaCloudError

from . import load_fixtures


async def test_json_request(
    aresponses: ResponsesMockServer,
    balena_cloud_client: BalenaCloud,
) -> None:
    """Test the JSON request method."""
    aresponses.add(
        "api.balena-cloud.com",
        "/v7/test",
        "GET",
        Response(
            status=200,
            headers={"Content-Type": "application/json"},
        ),
    )
    await balena_cloud_client._request("test")
    await balena_cloud_client.close()


async def test_internal_session(aresponses: ResponsesMockServer) -> None:
    """Test internal session is handled correctly."""
    aresponses.add(
        "api.balena-cloud.com",
        "/v7/test",
        "GET",
        Response(
            status=200,
            headers={"Content-Type": "application/json"},
        ),
    )
    async with BalenaCloud(token="FAKE_TOKEN") as client:  # noqa: S106
        await client._request("test")


async def test_timeout(aresponses: ResponsesMockServer) -> None:
    """Test request timeout is handled correctly."""

    # Faking a timeout by sleeping
    async def reponse_handler(_: ClientResponse) -> Response:
        await asyncio.sleep(0.2)
        return aresponses.Response(
            body="Goodmorning!",
        )

    aresponses.add("api.balena-cloud.com", "/v7/test", "GET", reponse_handler)

    async with ClientSession() as session:
        client = BalenaCloud(token="FAKE_TOKEN", session=session, request_timeout=0.1)  # noqa: S106
        with pytest.raises(BalenaCloudConnectionError):
            assert await client._request("test")


async def test_content_type(
    aresponses: ResponsesMockServer,
    balena_cloud_client: BalenaCloud,
) -> None:
    """Test request content type error is handled correctly."""
    aresponses.add(
        "api.balena-cloud.com",
        "/v7/test",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "blabla/blabla"},
            text=load_fixtures("no_data.json"),
        ),
    )
    with pytest.raises(BalenaCloudError):
        assert await balena_cloud_client._request("test")


async def test_client_error() -> None:
    """Test request client error is handled correctly."""
    async with ClientSession() as session:
        client = BalenaCloud(token="FAKE_TOKEN", session=session)  # noqa: S106
        with (
            patch.object(
                session,
                "request",
                side_effect=ClientError,
            ),
            pytest.raises(BalenaCloudConnectionError),
        ):
            assert await client._request("test")
