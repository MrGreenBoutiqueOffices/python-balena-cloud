"""Asynchronous Python client for Balena Cloud."""

from __future__ import annotations

import asyncio

from balena_cloud import BalenaCloud


async def main() -> None:
    """Show example of using the Balena Cloud API."""
    async with BalenaCloud(token="") as client:
        device_id: int = 1234567

        print("Get a device by ID")
        print("==================")
        device = await client.device.get(device_id=device_id)
        print(device)

        print()
        print("Change device name")
        print("==================")
        await client.device.update(
            device_id=device_id, data={"device_name": "My Device"}
        )
        new_device = await client.device.get(device_id=device_id)
        print(new_device)

        print()
        print(f"Revert device name to {device.name}")
        print("=================================")
        await client.device.update(
            device_id=device_id, data={"device_name": device.name}
        )
        device = await client.device.get(device_id=device_id)
        print(device)


if __name__ == "__main__":
    asyncio.run(main())
