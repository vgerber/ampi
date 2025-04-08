from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from app.services.devices_service import DevicesService, get_devices_service, DeviceData

devices_router = APIRouter(prefix="/devices")

DevicesServiceDep = Annotated[DevicesService, Depends(get_devices_service)]


@devices_router.get("")
def list_devices(
    devices_service: DevicesServiceDep, interface="wlan0"
) -> list[DeviceData]:
    return devices_service.get_devices(interface=interface)
