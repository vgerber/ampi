from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
import subprocess
import json
import requests
import websocket


class DeviceState(BaseModel):
    red: Optional[int] = None
    yellow: Optional[int] = None
    green: Optional[int] = None
    buzzer: Optional[int] = None
    signal: Optional[int] = None


class DeviceData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    ip: str
    name: str
    connection: Optional[websocket.WebSocket] = Field(default=None, exclude=True)

    @property
    def states(self) -> DeviceState:
        try:
            self.connection.send("{}")
            data = json.loads(self.connection.recv())
        except Exception:
            self._reconnect()
            self.connection.send("{}")
            data = json.loads(self.connection.recv())
        return DeviceState(**data)

    def set_states(self, states: DeviceState) -> DeviceState:
        payload = {
            key: value
            for key, value in states.model_dump().items()
            if value is not None and key != "signal"
        }
        try:
            self.connection.send(json.dumps(payload))
            data = json.loads(self.connection.recv())
        except Exception:
            self._reconnect()
            self.connection.send(json.dumps(payload))
            data = json.loads(self.connection.recv())
        return DeviceState(**data)

    def _reconnect(self):
        try:
            self.connection.close()
        except Exception:
            pass
        self.connection = websocket.create_connection(f"ws://{self.ip}/ws", timeout=5)
        self.connection.recv()  # consume initial state sent on connect


class DevicesService:
    def __init__(self):
        self.devices: dict[str, DeviceData] = {}

    def get_devices(self, interface="wlan0") -> list[DeviceData]:
        # Get devices connected to access point on interface
        arpa = subprocess.check_output(("arp", "-a")).decode("ascii")
        entries = arpa.split("\n")
        ips = [
            entry.split(" ")[1][1:-1]
            for entry in entries
            if entry.split(" ")[-1] == interface
        ]

        self.devices = {}

        for ip_address in ips:
            try:
                if not requests.get(
                    f"http://{ip_address}/ampi", timeout=3
                ).text.startswith("ampi-client"):
                    continue
                name = requests.get(f"http://{ip_address}/name").text
                connection = websocket.create_connection(
                    f"ws://{ip_address}/ws", timeout=5
                )
                connection.recv()  # consume initial state sent on connect
                self.devices[name] = DeviceData(
                    ip=ip_address, name=name, connection=connection
                )
            except Exception as error:
                print(error)
        return list(self.devices.values())

    def has_device(self, name: str) -> bool:
        return name in self.devices

    def get_device(self, name: str) -> DeviceData:
        return self.devices[name]

    def get_device_state(self, name: str) -> dict:
        return self.devices[name].states

    def set_device_state(self, name: str, states: dict) -> dict:
        return self.devices[name].set_states(states)


_devices_service = DevicesService()


def get_devices_service() -> DevicesService:
    return _devices_service
