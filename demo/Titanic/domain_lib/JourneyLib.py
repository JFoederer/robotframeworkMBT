#!/usr/bin/env python3
from robot.libraries.BuiltIn import BuiltIn
from robot.api.deco import keyword

from datetime import datetime, timedelta

from domain_lib.MapLib import MapLib
from simulation.titanic_in_ocean import TitanicInOcean
from simulation.journey import Journey

class JourneyLib:
    _journey = None

    def __init__(self):
        self.builtin = BuiltIn()

    @property
    def journey(self) -> Journey:
        if not self._journey:
            self._journey = Journey(self.map_lib.ocean)
        return self._journey

    @property
    def map_lib(self) -> MapLib:
        return self.builtin.get_library_instance("MapLib")

    @keyword("Start Journey on ${date}")
    def start_journey(self, date: str):
        date = datetime.strptime(date, "%Y-%m-%d")
        self.journey.start_date = date
        self.builtin.log(f"The journey has started at {self.journey.start_date}")

    @keyword("Current date of Journey")
    def journey_ondate(self):
        current_date: Date = self.journey.start_date + timedelta(minutes=self.journey.time_in_journey)
        return current_date.strftime('%Y-%m-%d')

    @keyword("play out Journey for a duration of ${minutes} minutes")
    def pass_time(self, minutes: int):
        """
        Progresses the journey by an x amount of minutes
        @param minutes: amount of minutes to progress the journey with.
        """
        self.journey.passed_time(minutes)

    @keyword("Move Titanic out of current area")
    def move_titanic_out_of_current_area(self):
        titanic = TitanicInOcean.instance
        current_area = self.builtin.run_keyword("Area of location Titanic's position")
        self.builtin.log(f"Titanic moving out of {current_area}")
        while (new_area := self.map_lib.get_area_of_location(titanic)) == current_area:
            if not titanic.speed > 0:
                self.builtin.log(f"Titanic not moving. Still in area {new_area}")
                break
            self.pass_time(1)
            if titanic.fell_off_the_earth():
                raise Exception("Titanic at least did not sink. But where did it go?")
        else:
            self.builtin.log(f"Titanic moved into {new_area}")
