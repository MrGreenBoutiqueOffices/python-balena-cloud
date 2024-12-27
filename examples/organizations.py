"""Asynchronous Python client for Balena Cloud."""

from __future__ import annotations

import asyncio

from balena_cloud import BalenaCloud


async def main() -> None:
    """Show example of using the Balena Cloud API."""
    async with BalenaCloud(token="") as client:
        print("Get all organizations")
        print("=====================")
        organizations = await client.get_organizations()
        for item in organizations:
            print(item)

        print()
        print("Get a organization by ID or handle")
        print("==================================")
        organization = await client.get_organization(org_handle=organizations[0].handle)
        print(organization)


if __name__ == "__main__":
    asyncio.run(main())
