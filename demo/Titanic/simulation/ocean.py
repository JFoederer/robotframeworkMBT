from typing import List, Any

from simulation.floating_object import FloatingObject
from simulation.location_on_grid import LocationOnGrid, AreaOnGrid

SECONDS_IN_MINUTE  = 60
COLLISION_INTERVAL = 10  # Following should hold True; SECONDS_IN_MINUTE % COLLISION_INTERVAL == 0


class Ocean:
    locations: dict[str, LocationOnGrid]
    areas: dict[str, AreaOnGrid]
    floating_objects: list[FloatingObject]

    def __init__(self):
        # self.locations = {}
        # self.areas = {}
        self.floating_objects = []

    def get_area_of_location(self, location: LocationOnGrid):
        for loc_name, loc in self.locations.items():
            if loc.distance_to(location) > self.LOCATION_AREA_THRESHOLD:
                return f"Area of ${loc_name}"

        for area_name, area in self.areas.items():
            if area.is_location_within_area(location):
                return area_name

        return self.ATLANTIC_AREA

    def minute_passes(self):
        """
        Make one minute pass. Check during every COLLISION_INTERVAL (in seconds) to see if a collision has happened.

        For every object that has collided in this minute, execute the corresponding collision method (@see FloatingObject.collided)
        """
        seconds_passed = 0
        floating_objects = set(self.floating_objects)
        objects_collided = set()
        while seconds_passed < SECONDS_IN_MINUTE:
            for floating_object in floating_objects:
                floating_object.update_coordinates(time_passed=COLLISION_INTERVAL)
                objects_collided.update(self.detect_collisions(collision_threshold=100))
                if objects_collided:
                    floating_objects.difference(objects_collided)
            seconds_passed += COLLISION_INTERVAL
        for obj in objects_collided:
            print(f"{obj} has collided with another object")
            obj.collided()

    def detect_collisions(self, collision_threshold: int, speed_threshold: int = 0):
        """
        @param collision_threshold: Threshold in meters for when two objects have collided
        @param speed_threshold: Threshold in knots. If 2 items are stationary they do not really collide
        """
        objects_collided = set()
        for i in range(len(self.floating_objects)):
            for j in range(i + 1, len(self.floating_objects)):
                object1 = self.floating_objects[i]
                object2 = self.floating_objects[j]

                distance = object1.distance_to(object2)

                speed = object1.speed + object2.speed

                if distance < collision_threshold and speed > speed_threshold:
                    objects_collided.add(object1)
                    objects_collided.add(object2)

        return objects_collided
