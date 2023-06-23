#!/usr/bin/env python3
from robot.libraries.BuiltIn import BuiltIn

from system.titanic import Titanic
from simulation.iceberg import Iceberg
from simulation.titanic_in_ocean import TitanicInOcean
from simulation.journey import Journey
from simulation.ocean import Ocean
from robot.api.deco import keyword


class JourneyLib:
    def __init__(self):
        self.builtin = BuiltIn()
        self.ocean = Ocean()
        self.journey = Journey(self.ocean)

    @property
    def map_lib(self):
        return self.builtin.get_library_instance("MapLib")

    @keyword("Spawn titanic at location ${location}")
    def spawn_titanic(self, location: str):
        """
        Spawns the titanic with given parameters
        @param location: location of titanic
        """
        location = self.builtin.run_keyword(f"Location of port {location}")
        t = Titanic(0, steering_direction=0)
        tio = TitanicInOcean(t, location.longitude, location.latitude, 0, 0)
        self.ocean.floating_objects.append(tio)

    @keyword("Spawn iceberg at coordinate long ${long} lat ${lat}")
    def spawn_iceberg(self, long: float, lat: float):
        """
        Spawns an iceberg with given parameters
        @param long: longitude of iceberg
        @param lat: latitude of iceberg
        """
        iceberg = Iceberg(long, lat)
        self.ocean.floating_objects.append(iceberg)

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
        current_area = self.builtin.run_keyword("Area of location Titanic's location")
        print(f"Titanic moving out of {current_area}")
        while (new_area := self.map_lib.get_area_of_location(titanic)) == current_area:
            assert titanic.speed > 0
            self.pass_time(1)
            if titanic.fell_off_the_earth():
                raise Exception("Titanic at least did not sink. But where did it go?")
        print(f"Titanic moved into {new_area}")
