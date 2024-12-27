"""Asynchronous Python client for Balena Cloud."""

from __future__ import annotations

import asyncio

from balena_cloud import BalenaCloud


async def main() -> None:
    """Show example of using the Balena Cloud API."""
    async with BalenaCloud(token="") as client:
        device_id: int = 1234567

        print("Get a tags from a device")
        print("========================")
        tags = await client.get_device_tags(device_id=device_id)
        print(tags)

        print()
        print("Create a tag for a device")
        print("=========================")
        await client.add_device_tag(device_id=device_id, key="test", value="test")
        tags = await client.get_device_tags(device_id=device_id)
        print(tags)

        print()
        print("Change a tag from a device")
        print("===========================")
        await client.update_device_tag(
            device_id=device_id, key="test", value="new value"
        )
        tags = await client.get_device_tags(device_id=device_id)
        print(tags)

        print()
        print("Delete a tag from a device")
        print("===========================")
        await client.remove_device_tag(tag_id=tags[0].id)
        tags = await client.get_device_tags(device_id=device_id)
        print(tags)


if __name__ == "__main__":
    asyncio.run(main())
