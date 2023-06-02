from system.titanic import Titanic
from enum import Enum


class StatusOfJourney(Enum):
    READY_FOR_DEPARTURE = 1
    ON_THE_WAY = 2
    ARRIVED = 3
    SUNK = 4


class Journey:
    def __init__(self, ocean):
        self.time_in_journey = 0
        self.status = StatusOfJourney.READY_FOR_DEPARTURE
        self.ocean = ocean

    def __repr__(self):
        return f"{type(self).__name__}, ({self.__class__.__name__} (status={self.status.name}))"

    def passed_time(self, time_unit):
        for i in range(0, time_unit):
            for object_in_ocean in self.ocean.floating_objects:
                object_in_ocean.update_position()
                print(f"{object_in_ocean}, new position={object_in_ocean.position}")
        self.time_in_journey += time_unit
