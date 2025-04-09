from pydantic import BaseModel
import subprocess
import requests

class DeviceData(BaseModel):
    def __init__(self, ip: str, name: str):
        self.ip = ip
        self.name = name

    @property
    def states(self) -> dict:
        return requests.get(f"http://{self.ip}/states").json()

    def set_states(self, states: dict) -> dict:
        return requests.patch(f"http://{self.ip}/states", json=states).json()

class DevicesService:
    def __init__(self):
        self.devices: dict[str, DeviceData] = {}

    def get_devices(self, interface="wlan0") -> list[DeviceData]:
        # Get devices connected to access point on interface
        arpa = subprocess.check_output(("arp", "-a")).decode("ascii")
        entries = arpa.split("\n")
        ips = [e.split(" ")[1][1:-1] for e in entries if e.split(" ")[-1] == interface]

        self.devices = {}

        for ip in ips:
            try:
                if not requests.get(f"http://{ip}/ampi", timeout=3).text.startswith(
                    "ampi-client"
                ):
                    continue
                name = requests.get(f"http://{ip}/name").text
                self.devices[name] = DeviceData(ip=ip, name=name)
            except Exception as ex:
                print(ex)
        return list(self.devices.values())

    def has_device(self, name: str) -> bool:
        return name in self.devices

    def get_device_ip(self, name: str) -> str | None:
        return self.devices[name].ip
    
    def get_device_state(self, name: str) -> dict:
        return self.devices[name].states
    
    def set_device_state(self, name: str, states: dict) -> dict:
        return self.devices[name].set_states(states)


_devices_service = DevicesService()


def get_devices_service() -> DevicesService:
    return _devices_service
