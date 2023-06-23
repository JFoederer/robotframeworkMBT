import math
from abc import abstractmethod

from simulation.location_on_grid import LocationOnGrid


class FloatingObject(LocationOnGrid):

    def __init__(self, longitude, latitude, speed, direction):
        super().__init__(longitude, latitude)
        self.speed = speed  # speed knots
        self.direction = direction  # direction in degrees

    @abstractmethod
    def collided(self):  # TODO expand with parameter to indicate what is hit (e.g. to distinguish between iceberg size)
        """Method to execute when this object has collided with another FloatingObject"""

    def update_coordinates(self, time_passed=10):
        """
        Update longitude/latitude coordinates based on time passed, speed and direction
        @param time_passed: time passed in seconds
        """
        # Convert latitude and longitude to radians
        latitude_rad = math.radians(self.latitude)
        longitude_rad = math.radians(self.longitude)

        # Convert speed from knots to meters per second
        speed_mps = self.speed * 0.514444

        # Calculate the distance traveled in 10 seconds
        distance = speed_mps * time_passed

        # Calculate the new latitude and longitude based on the direction
        new_latitude_rad = math.asin(math.sin(latitude_rad) * math.cos(distance / self.EARTH_RADIUS) +
                                     math.cos(latitude_rad) * math.sin(distance / self.EARTH_RADIUS) *
                                     math.cos(math.radians(self.direction)))

        new_longitude_rad = longitude_rad + math.atan2(math.sin(math.radians(self.direction)) *
                                                       math.sin(distance / self.EARTH_RADIUS) *
                                                       math.cos(latitude_rad),
                                                       math.cos(distance / self.EARTH_RADIUS) -
                                                       math.sin(latitude_rad) *
                                                       math.sin(new_latitude_rad))

        # Convert back to degrees
        new_latitude = math.degrees(new_latitude_rad)
        new_longitude = math.degrees(new_longitude_rad)

        # Update the object's coordinates
        self.latitude = new_latitude
        self.longitude = new_longitude

    def __repr__(self):
        return f"{type(self).__name__} (speed={self.speed}, direction={self.direction}, position={self.longitude}, {self.latitude})"
