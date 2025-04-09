from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Body
from app.services.devices_service import DevicesService, get_devices_service, DeviceData

devices_router = APIRouter(prefix="/devices")

DevicesServiceDep = Annotated[DevicesService, Depends(get_devices_service)]


@devices_router.get("")
def list_devices(
    devices_service: DevicesServiceDep, interface="wlan0"
) -> list[DeviceData]:
    return devices_service.get_devices(interface=interface)


@devices_router.get("/{device_name}/states")
def get_device_states(
    device_name: str,
    devices_service: DevicesServiceDep, 
) -> dict:
    if not devices_service.has_device(device_name):
        raise HTTPException(status_code=404, detail=f"Device {device_name} not found")
    return devices_service.get_device_state(device_name)

@devices_router.patch("/{device_name}/states", status_code=200)
def update_device_states(
    device_name: str,
    devices_service: DevicesServiceDep, 
    states: dict = Body(default={ "red": 1 }),
) -> dict:
    if not devices_service.has_device(device_name):
        raise HTTPException(status_code=404, detail=f"Device {device_name} not found")
    return devices_service.set_device_state(device_name, states=states)