import math


class LocationOnGrid:

    EARTH_RADIUS = 6371000

    def __init__(self, longitude, latitude):
        self.longitude = longitude
        self.latitude = latitude

    def __str__(self):
        return f"{'N' if self.longitude >= 0 else 'S'}{abs(self.longitude):08.5f} "\
               f"{'E' if self.latitude >= 0 else 'W'}{abs(self.latitude):08.5f}"

    def distance_to(self, other_object: 'LocationOnGrid'):
        """
        Calculate the distance to another floating object based on its longitude/latitude coordinates
        @param other_object: The FloatingObject to compare
        @return: distance in meters to the other floating object
        """
        return math.sqrt((other_object.longitude - self.longitude) ** 2 + (other_object.latitude - self.latitude) ** 2)

    def calculate_direction(self, other_point: 'LocationOnGrid'):
        x1, y1 = (self.longitude, self.latitude)
        x2, y2 = (other_point.longitude, other_point.latitude)

        # Calculate the differences in x and y coordinates
        dx = x2 - x1
        dy = y2 - y1

        # Calculate the angle in radians
        angle = math.atan2(dy, dx)

        # Convert the angle to degrees
        degrees = math.degrees(angle)

        # Adjust the range of degrees to be between 0 and 360
        adjusted_degrees = (degrees + 360) % 360

        # Return the direction in degrees
        return adjusted_degrees


class AreaOnGrid:

    def __init__(self, upper_left_bound: LocationOnGrid, lower_right_bound: LocationOnGrid):
        self.upper_left_bound = upper_left_bound
        self.lower_right_bound = lower_right_bound

    def is_location_within_area(self, location: LocationOnGrid):
        return self.upper_left_bound.longitude <= location.longitude <= self.lower_right_bound.longitude and \
            self.lower_right_bound.latitude <= location.latitude <= self.upper_left_bound.latitude
