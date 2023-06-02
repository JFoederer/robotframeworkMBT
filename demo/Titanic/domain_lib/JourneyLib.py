#!/usr/bin/env python3

from simulation.floating_object import FloatingObject
from system.titanic import Titanic
from simulation.iceberg import Iceberg
from simulation.titanic_in_ocean import TitanicInOcean
from simulation.journey import Journey
from simulation.ocean import Ocean
from robot.api.deco import keyword

class JourneyLib():
    def __init__(self):
        self.ocean = Ocean()

    @keyword("Spawn titanic at coordinate N${n} W${w} with a heading of ${heading} and at speed of ${speed} knots")
    def spawn(self, n, w, heading, speed):
        t = Titanic(speed, "east")
        tio = TitanicInOcean(t, n, w, speed, "west")
        self.ocean.floating_objects.append(tio)
        
    @keyword("Spawn iceberg at coordinate N${n} W${w}")
    def spawn_iceberg(self, n, w):
        iceberg = Iceberg(n, w)
        self.ocean.floating_objects.append(iceberg)

    @keyword("Pass time")
    def pass_time(self):
        j = Journey(self.ocean)
        j.passed_time(10)

