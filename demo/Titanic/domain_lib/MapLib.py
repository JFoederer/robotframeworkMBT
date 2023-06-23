#!/usr/bin/env python3
from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn

from simulation.location_on_grid import LocationOnGrid, AreaOnGrid
from simulation.ocean import Ocean


class MapLib:
    def __init__(self):
        self.builtin = BuiltIn()

    locations = {
        'Southampton': LocationOnGrid(50.909698, -1.404351),
        'Cherbourg': LocationOnGrid(49.630001, -1.620000),
        'Queenstown': LocationOnGrid(51.850334, -8.294286),
        'New York': LocationOnGrid(40.730610, -73.935242)
    }

    areas = {
        'the English Channel': AreaOnGrid(LocationOnGrid(49.5, -1.41), LocationOnGrid(51.9, -8.2)),
        'Iceberg': AreaOnGrid(LocationOnGrid(43, -45), LocationOnGrid(48, -50))
    }

    atlantic_area = AreaOnGrid(LocationOnGrid(51.9, -74), LocationOnGrid(40, -1.41))

    LOCATION_AREA_THRESHOLD = 0.1
    ATLANTIC_AREA = 'Atlantic'

    @keyword("Location of port ${harbour}")
    def location_of_(self, harbour):
        return self.locations[harbour]

    @keyword("Area of location ${location}")
    def get_area_of_location(self, location: LocationOnGrid):
        if isinstance(location, str):
            location = self.builtin.run_keyword(location)
        for loc_name, loc in self.locations.items():
            if loc.distance_to(location) < self.LOCATION_AREA_THRESHOLD:
                return f"Area of ${loc_name}"

        for area_name, area in self.areas.items():
            if area.is_location_within_area(location):
                return area_name

        return self.ATLANTIC_AREA

    @keyword("${object_location} is within the Map area of ${area_name}")
    def is_within_area(self, object_location, area_name):
        if isinstance(object_location, str):
            object_location = self.builtin.run_keyword(object_location)
        if area_name in self.areas:
            return self.areas[area_name].is_location_within_area(object_location)
        elif area_name in self.locations:
            return self.locations[area_name].distance_to(object_location) < self.LOCATION_AREA_THRESHOLD
        else:
            raise AttributeError(f"Area {area_name} does not exist")
