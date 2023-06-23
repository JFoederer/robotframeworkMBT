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
        # Convert direction from degrees to radians
        direction_rad = math.radians(self.direction)

        # Calculate the distance traveled using speed and time
        distance = (self.speed / self.EARTH_RADIUS) * time_passed

        # Calculate the horizontal and vertical displacements
        delta_x = distance * math.cos(direction_rad)
        delta_y = distance * math.sin(direction_rad)

        # Update the coordinates of the point
        self.longitude += delta_x
        self.latitude += delta_y

    def __repr__(self):
        return f"{type(self).__name__} (speed={self.speed}, direction={self.direction}, position={self.longitude}, {self.latitude})"
