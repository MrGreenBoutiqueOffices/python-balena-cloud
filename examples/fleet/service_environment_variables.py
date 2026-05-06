"""Asynchronous Python client for Balena Cloud."""

from __future__ import annotations

import asyncio

from balena_cloud import BalenaCloud


async def main() -> None:
    """Show example of using the Balena Cloud API."""
    async with BalenaCloud(token="") as client:
        service_id: int = 1234567

        print("Get service environment variables from a fleet service")
        print("======================================================")
        env_variables = await client.fleet_service_variable.get_all(
            service_id=service_id
        )
        print(env_variables)

        print()
        print("Get single service environment variable")
        print("=======================================")
        env_variable = await client.fleet_service_variable.get(
            variable_id=env_variables[0].id
        )
        print(env_variable)

        print()
        print("Add a service environment variable to a fleet")
        print("=============================================")
        await client.fleet_service_variable.add(
            service_id=service_id,
            name="MY_ENV_VAR",
            value="my_value",
        )
        env_variables = await client.fleet_service_variable.get_all(
            service_id=service_id
        )
        print(env_variables)

        print()
        print("Update a service environment variable from a fleet")
        print("==================================================")
        await client.fleet_service_variable.update(
            variable_id=env_variables[0].id, value="new_value"
        )
        env_variables = await client.fleet_service_variable.get_all(
            service_id=service_id
        )
        print(env_variables)

        print()
        print("Delete a service environment variable from a fleet")
        print("==================================================")
        await client.fleet_service_variable.remove(variable_id=env_variables[0].id)
        env_variables = await client.fleet_service_variable.get_all(
            service_id=service_id
        )
        print(env_variables)


if __name__ == "__main__":
    asyncio.run(main())
