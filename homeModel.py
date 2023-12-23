from typing import Dict, Callable
from environment import Environment
from deviceModels import SmartDevice

class Room:
    def __init__(self, env: Environment, name: str, temperature: float = 20) -> None:
        self.env = env
        self.name = name if name else "Unnamed"
        self.temperature = temperature  # Celsius
        self.devices: Dict[str, SmartDevice] = {}

    def add_device(self, device: SmartDevice) -> None:
        if device.name in self.devices:
            raise ValueError(f"Room {self.name} already has a device called {device.name}!")
        self.devices[device.name] = device

    def get_device(self, device_name: str) -> SmartDevice:
        if device_name not in self.devices:
            raise ValueError(f"Room {self.name} does not have a device called {device_name}!")
        return self.devices[device_name]


class Home:
    def __init__(self, env: Environment) -> None:
        self.env = env
        self.rooms: Dict[str, Room] = {}

    def add_room(self, room: Room) -> None:
        if room.name in self.rooms:
            raise ValueError(f"Home already has a room called {room.name}!")
        self.rooms[room.name] = room

    def go_to_room(self, room_name: str, inhabitant_name: str) -> Room:
        '''Returns the room with the given name. Publishes an event that the inhabitant went to the room.'''
        if room_name not in self.rooms:
            raise ValueError(f"Home does not have a room called {room_name}!")
        self.env.eventHandler.publish("inhabitant_goes_to_room", inhabitant_name, room_name)
        print(f"{inhabitant_name} | -> {room_name}")
        return self.rooms[room_name]
    
    def get_device_op(self, room_name: str, device_name: str, operation_name: str) -> Callable:
        if room_name not in self.rooms:
            raise ValueError(f"Home does not have a room called {room_name}!")
        return self.rooms[room_name].get_device(device_name).opMap[operation_name]