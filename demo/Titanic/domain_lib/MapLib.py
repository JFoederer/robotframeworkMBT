#!/usr/bin/env python3
from robot.api.deco import keyword
from collections import OrderedDict

from simulation.location_on_grid import LocationOnGrid, AreaOnGrid
from simulation.ocean import Ocean
from simulation.titanic_in_ocean import TitanicInOcean


class MapLib:

    locations = {
        'South Hampton': LocationOnGrid(50,909698, -1.404351),
        'Cherbourg': LocationOnGrid(49.630001, -1.620000),
        'Queenstown': LocationOnGrid(51.850334, -8.294286),
        'New York': LocationOnGrid(40.730610, -73.935242)
    }

    areas = {
        'Channel': AreaOnGrid(LocationOnGrid(51.9, -8.2), LocationOnGrid(49.5, -1.41)),
        'Iceberg': AreaOnGrid(LocationOnGrid(48, -50), LocationOnGrid(43, -45))
    }

    atlantic_area = AreaOnGrid(LocationOnGrid(51.9, -74), LocationOnGrid(40, -1.41))

    LOCATION_AREA_THRESHOLD = 0.1

    @keyword("Location of ${harbour}")
    def location_of_(self, harbour ):
        return self.locations[harbour]

    @keyword("'${object_location}' is within the Map area of '${area_name}'")
    def provide_current_area_where_titanic_is(self, object_location: LocationOnGrid, area_name: str):
        for loc_name, object_location in self.locations.items():
            if object_location.distance_to(location) > self.LOCATION_AREA_THRESHOLD:
                return f"Area of ${loc_name}"

        for area_name, area in self.areas.items():
            if area.is_location_within_area(location):
                return area_name

        if not self.atlantic_area.is_location_within_area(location):
            raise Exception("Not in Atlantic ocean area")