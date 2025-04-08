from importlib import import_module
from typing import Annotated
from pydantic import BaseModel, Field
import subprocess
import requests


class DeviceData(BaseModel):
    def __init__(self, ip: str, name: str):
        self.ip = ip
        self.name = name


class DevicesService:
    def __init__(self):
        self.devices: list[DeviceData] = []

    def get_devices(self, interface="wlan0") -> list[DeviceData]:
        arpa = subprocess.check_output(("arp", "-a")).decode("ascii")
        entries = arpa.split("\n")
        ips = [e.split(" ")[1][1:-1] for e in entries if e.split(" ")[-1] == interface]

        devices = []
        for ip in ips:
            try:
                if not requests.get(f"http://{ip}/ampi", timeout=1).text.startswith(
                    "ampi-client"
                ):
                    continue
                name = requests.get(f"http://{ip}/name").text
                devices.append(DeviceData(ip, name))
            except Exception as _:
                pass
        self.devices = devices
        return devices

    def get_device_ip(self, name: str) -> str | None:
        for device in self.devices:
            if device.name == name:
                return device.ip
        return None


_devices_service = DevicesService()


def get_devices_service() -> DevicesService:
    return _devices_service
