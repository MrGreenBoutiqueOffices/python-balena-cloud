"""Asynchronous Python client for Balena Cloud."""

from __future__ import annotations

import asyncio

from balena_cloud import BalenaCloud


async def main() -> None:
    """Show example of using the Balena Cloud API."""
    async with BalenaCloud(token="") as client:
        device_id: int = 1234567

        print("Get environment variables from a device")
        print("=======================================")
        env_variables = await client.device_variable.get_all(device_id=device_id)
        print(env_variables)

        print()
        print("Get single environment variable")
        print("===============================")
        env_variable = await client.device_variable.get(variable_id=env_variables[0].id)
        print(env_variable)

        print()
        print("Add an environment variable to a device")
        print("=======================================")
        await client.device_variable.add(
            device_id=device_id, name="MY_ENV_VAR", value="my_value"
        )
        env_variables = await client.device_variable.get_all(device_id=device_id)
        print(env_variables)

        print()
        print("Update an environment variable from a device")
        print("============================================")
        await client.device_variable.update(
            variable_id=env_variables[0].id, value="new_value"
        )
        env_variables = await client.device_variable.get_all(device_id=device_id)
        print(env_variables)

        print()
        print("Delete an environment variable from a device")
        print("============================================")
        await client.device_variable.remove(variable_id=env_variables[0].id)
        env_variables = await client.device_variable.get_all(device_id=device_id)
        print(env_variables)


if __name__ == "__main__":
    asyncio.run(main())
