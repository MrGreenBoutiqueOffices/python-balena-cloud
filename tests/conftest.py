"""Fixture for the Balena Cloud tests."""

from collections.abc import AsyncGenerator

import pytest
from aiohttp import ClientSession

from balena_cloud import BalenaCloud


@pytest.fixture(name="balena_cloud_client")
async def client() -> AsyncGenerator[BalenaCloud, None]:
    """Create a Balena Cloud client."""
    async with (
        ClientSession() as session,
        BalenaCloud(token="API_TOKEN", session=session) as balena_cloud_client,  # noqa: S106
    ):
        yield balena_cloud_client
