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
        for organization in organizations:
            print(organization)

        print()
        print("Get a organization by ID or handle")
        print("==================================")
        organization = await client.get_organization(org_handle=organizations[0].handle)
        print(organization)

        print()
        print("Getting all fleets from the organization:")
        print("=========================================")
        fleets = await client.get_organization_fleets(org_handle=organization.handle)
        for fleet in fleets:
            print(fleet)


if __name__ == "__main__":
    asyncio.run(main())
