#!/usr/bin/env python3
from robotnl import keyword
from robot.libraries.BuiltIn import BuiltIn

from simulation.map_animation import map_animation
from simulation.iceberg import Iceberg
from simulation.location_on_grid import LocationOnGrid, AreaOnGrid
from simulation.ocean import Ocean
from simulation.titanic_in_ocean import TitanicInOcean
from system.titanic import Titanic


class MapLib:

    ocean = Ocean()

    def __init__(self):
        self.builtin = BuiltIn()

    locations = {
        'Southampton': LocationOnGrid(latitude=50.909698, longitude=-1.404351),
        'Cherbourg': LocationOnGrid(latitude=49.630001, longitude=-1.620000),
        'Queenstown': LocationOnGrid(latitude=51.850334, longitude=-8.294286),
        'Plymouth': LocationOnGrid(latitude=49.51036, longitude=-5.14305),
        'New York': LocationOnGrid(latitude=40.730610, longitude=-73.935242)
    }

    areas = {
        'the English Channel': AreaOnGrid(LocationOnGrid(latitude=49.5, longitude=-1.35), LocationOnGrid(latitude=51.850334, longitude=-8.294286)),
        'Iceberg alley': AreaOnGrid(LocationOnGrid(latitude=43, longitude=-45), LocationOnGrid(latitude=48, longitude=-50))
    }

    atlantic_area = AreaOnGrid(LocationOnGrid(latitude=35, longitude=-1.41), LocationOnGrid(latitude=65, longitude=-74))

    LOCATION_AREA_THRESHOLD = 0.1
    ATLANTIC_AREA = 'Atlantic'

    @keyword("Enable map animation")
    def enable_animation(self):
        draw_areas = self.areas.copy()
        draw_areas['Atlantic Ocean'] = self.atlantic_area
        map_animation.plot_static_elements(draw_areas, self.locations)

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

    @keyword("Spawn iceberg at coordinate latitude ${lat} longitude ${long}")
    def spawn_iceberg(self, lat: float, long: float):
        """
        Spawns an iceberg with given parameters
        @param lat: latitude of iceberg
        @param long: longitude of iceberg
        """
        iceberg = Iceberg(longitude=long, latitude=lat)
        if isinstance(self.ocean.floating_objects[-1], Iceberg):
            self.ocean.floating_objects[-1] = iceberg
        else:
            self.ocean.floating_objects.append(iceberg)

    @keyword("Location of port ${harbour}")
    def location_of_(self, harbour):
        return self.locations[harbour]

    @keyword("Area of location ${location}")
    def get_area_of_location(self, location: LocationOnGrid):
        for loc_name, loc in self.locations.items():
            if loc.distance_to(location) < self.LOCATION_AREA_THRESHOLD:
                return f"Area of {loc_name}"

        for area_name, area in self.areas.items():
            if area.is_location_within_area(location):
                return area_name

        return self.ATLANTIC_AREA

    @keyword("Map area where '${position}' is located")
    def area_by_position(self, position):
        for area_name in self.locations:
            if self.locations[area_name].distance_to(position) < self.LOCATION_AREA_THRESHOLD:
                return area_name
        for area_name in self.areas:
            if self.areas[area_name].is_location_within_area(position):
                return area_name
        return 'Atlantic ocean'
