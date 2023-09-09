#!/usr/bin/env python3
from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn

from simulation.location_on_grid import LocationOnGrid
from simulation.titanic_in_ocean import TitanicInOcean


class TitanicLib:
    def __init__(self):
        self.builtin = BuiltIn()

    @keyword("Titanic is sinking")
    def titanic_is_sinking(self):
        """
        Reports whether the titanic is sinking or not.
        @return: bool indicating sunk status of the Titanic in the ocean.
        """
        return TitanicInOcean.instance.sunk

    @keyword("Point titanic towards location ${location}")
    def point_titanic_towards(self, location):
        titanic = TitanicInOcean.instance
        port_location = self.builtin.run_keyword(f"Location of port {location}")
        new_direction = titanic.calculate_direction(port_location)

        titanic.direction = new_direction
        self.builtin.log(f"Titanic moves to {location}")

    @keyword("Titanic stops")
    def titanic_stops(self):
        titanic = TitanicInOcean.instance
        titanic.titanic.throttle = 0
        titanic.speed = 0  # TODO should happen over time (due to throttle being > 0)
        self.builtin.log("Now it is time for Titanic to stop at new location")

    @keyword("Titanic moves full speed ahead")
    def titanic_full_speed(self):
        titanic = TitanicInOcean.instance
        titanic.titanic.throttle = 1
        titanic.speed = 700  # TODO Figure out what this speed means. Does time calculation make sense?!?!
        self.builtin.log(f"Here we go through the new location with speed {titanic.speed}")

    @keyword("Titanic's position")
    def titanic_location(self):
        titanic = TitanicInOcean.instance
        loc = LocationOnGrid(titanic.longitude, titanic.latitude)
        self.builtin.log(f"Titanic's current position is: {loc}")
        return loc

    @keyword("Titanic's speed")
    def titanic_speed(self):
        titanic = TitanicInOcean.instance
        self.builtin.log(f"Titanic's current speed is: {titanic.speed}")
        return titanic.speed
