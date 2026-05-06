"""Resource clients for the Balena Cloud API."""

from .device import (
    DeviceResource,
    DeviceServiceVariableResource,
    DeviceTagResource,
    DeviceVariableResource,
    ServiceInstallResource,
)
from .fleet import FleetResource, FleetServiceVariableResource, ServiceResource
from .organization import OrganizationResource
from .release import ReleaseResource

__all__ = [
    "DeviceResource",
    "DeviceServiceVariableResource",
    "DeviceTagResource",
    "DeviceVariableResource",
    "FleetResource",
    "FleetServiceVariableResource",
    "OrganizationResource",
    "ReleaseResource",
    "ServiceInstallResource",
    "ServiceResource",
]
