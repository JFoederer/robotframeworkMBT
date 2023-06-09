from __future__ import annotations

import math
from abc import abstractmethod

EARTH_RADIUS = 6371000


class FloatingObject:

    def __init__(self, latitude, longitude, speed, direction):
        self.latitude = latitude
        self.longitude = longitude
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
        new_latitude_rad = math.asin(math.sin(latitude_rad) * math.cos(distance / EARTH_RADIUS) +
                                     math.cos(latitude_rad) * math.sin(distance / EARTH_RADIUS) *
                                     math.cos(math.radians(self.direction)))

        new_longitude_rad = longitude_rad + math.atan2(math.sin(math.radians(self.direction)) *
                                                       math.sin(distance / EARTH_RADIUS) *
                                                       math.cos(latitude_rad),
                                                       math.cos(distance / EARTH_RADIUS) -
                                                       math.sin(latitude_rad) *
                                                       math.sin(new_latitude_rad))

        # Convert back to degrees
        new_latitude = math.degrees(new_latitude_rad)
        new_longitude = math.degrees(new_longitude_rad)

        # Update the object's coordinates
        self.latitude = new_latitude
        self.longitude = new_longitude

    def distance_to(self, other_object: FloatingObject):
        """
        Calculate the distance to another floating object based on its longitude/latitude coordinates
        @param other_object: The FloatingObject to compare
        @return: distance in meters to the other floating object
        """
        # Convert latitude and longitude to radians
        lat1 = math.radians(self.latitude)
        lon1 = math.radians(self.longitude)
        lat2 = math.radians(other_object.latitude)
        lon2 = math.radians(other_object.longitude)

        # Calculate the differences in latitudes and longitudes
        delta_lat = lat2 - lat1
        delta_lon = lon2 - lon1

        # Use the haversine formula to calculate the distance
        a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = EARTH_RADIUS * c

        return distance

    def __repr__(self):
        return f"{type(self).__name__} (speed={self.speed}, direction={self.direction}, position={self.longitude}, {self.latitude})"
