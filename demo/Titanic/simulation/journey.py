from simulation.ocean import Ocean
from enum import Enum

from simulation.titanic_in_ocean import TitanicInOcean


class StatusOfJourney(Enum):
    READY_FOR_DEPARTURE = 1
    ON_THE_WAY = 2
    ARRIVED = 3
    SUNK = 4


class Journey:
    ocean: Ocean

    def __init__(self, ocean):
        self.time_in_journey = 0  # minutes
        self.status = StatusOfJourney.READY_FOR_DEPARTURE
        self.ocean = ocean

    def __repr__(self):
        return f"{type(self).__name__}, ({self.__class__.__name__} (status={self.status.name}))"

    def passed_time(self, time_unit):
        """
        Passes time of the journey
        @param time_unit: amount of minutes to pass the journey with
        """
        for i in range(0, time_unit):
            self.ocean.minute_passes()
        self.time_in_journey += time_unit
