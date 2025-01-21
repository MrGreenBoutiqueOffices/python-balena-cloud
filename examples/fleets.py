"""Asynchronous Python client for Balena Cloud."""

from __future__ import annotations

import asyncio

from balena_cloud import BalenaCloud, Device, Fleet


async def main() -> None:
    """Show example of using the Balena Cloud API."""
    async with BalenaCloud(token="") as client:
        fleet_id: int = 1234567

        print("Get all fleets")
        print("==============")
        fleets: list[Fleet] = await client.get_fleets()
        for fleet in fleets:
            print(fleet)

        print()
        print("Get a fleet by ID, slug, or name")
        print("================================")
        fleet = await client.get_fleet(fleet_id=fleets[0].id)
        print(fleet)

        print()
        print("Getting all devices from a fleet:")
        print("=================================")

        devices: list[Device] = await client.get_fleet_devices(fleet_id=fleet_id)
        for device in devices:
            print(device)


if __name__ == "__main__":
    asyncio.run(main())
