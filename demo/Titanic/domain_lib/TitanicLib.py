#!/usr/bin/env python3
from robot.api.deco import keyword

from simulation.location_on_grid import LocationOnGrid
from simulation.ocean import Ocean
from simulation.titanic_in_ocean import TitanicInOcean


class TitanicLib:

    # @keyword("Titanic is docked in ${location}")
    # def titanic_is_docked_in(self, location):
    #     return (TitanicInOcean.instance.longitude, TitanicInOcean.instance.latitude) == Ocean.locations[location]

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
        new_direction = titanic.calculate_direction(Ocean.locations[location])

        titanic.direction = new_direction

    @keyword("Titanic stops")
    def titanic_stops(self):
        titanic = TitanicInOcean.instance
        titanic.titanic.throttle = 0
        titanic.speed = 0  # TODO should happen over time (due to throttle being > 0)

    @keyword("Titanic moves full speed ahead")
    def titanic_full_speed(self):
        titanic = TitanicInOcean.instance
        titanic.titanic.throttle = 1
        titanic.speed = 1  # TODO should happen over time (due to throttle being > 0)

    @keyword("Titanic's location")
    def titanic_location(self):
        titanic = TitanicInOcean.instance
        loc = LocationOnGrid(titanic.longitude, titanic.latitude)
        return loc

    @keyword("Titanic's speed")
    def titanic_speed(self):
        titanic = TitanicInOcean.instance
        return titanic.speed
