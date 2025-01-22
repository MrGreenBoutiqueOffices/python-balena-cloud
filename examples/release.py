"""Asynchronous Python client for Balena Cloud."""

from __future__ import annotations

import asyncio

from balena_cloud import BalenaCloud, Release


async def main() -> None:
    """Show example of using the Balena Cloud API."""
    async with BalenaCloud(token="") as client:
        fleet_id: int = 1234567
        release_id: int = 1234567

        print("Get all releases from a fleet")
        print("=============================")
        releases: list[Release] = await client.get_fleet_releases(fleet_id=fleet_id)
        for item in releases:
            print(item)

        print()
        print("Get a release by ID")
        print("===================")
        release = await client.get_release(release_id=releases[0].id)
        print(release)

        print()
        print("Get filtered releases from a fleet")
        print("===================================")
        filtered_releases: list[Release] = await client.get_fleet_releases(
            fleet_id=fleet_id, filters={"is_final": False}
        )
        for release in filtered_releases:
            print(release)

        print()
        print("Delete a release")
        print("================")
        await client.remove_release(release_id=release_id)
        print(f"Release {release_id} deleted")


if __name__ == "__main__":
    asyncio.run(main())
