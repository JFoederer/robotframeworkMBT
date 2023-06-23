from __future__ import annotations

from simulation.floating_object import FloatingObject


class TitanicInOcean(FloatingObject):

    instance: TitanicInOcean = None

    def __new__(cls, titanic, longitude, latitude, speed, direction, sunk=False):
        if not cls.instance:
            cls.instance = super(TitanicInOcean, cls).__new__(cls)
        return cls.instance

    def __init__(self, titanic, longitude, latitude, speed, direction):
        super().__init__(longitude, latitude, speed, direction)
        self.sunk = False
        self.titanic = titanic

    def update_coordinates(self, time_passed=10):
        # TODO Take into account the steering_direction of the titanic
        # TODO Take into account the throttle of the titanic (i.e.: should start decreasing speed when throttle is 0)
        return super().update_coordinates(time_passed)

    def collided(self):
        """
        Emulate what happens when Titanic hits another object in the sea.
        Loses all speed, sets titanic's damage flag to True and sets the sunk flag to True
        """
        self.speed = 0

        self.titanic.damaged = True
        # TODO First the titanic will take damage. As time passes it will sink.
        self.sunk = True

    def fell_off_the_earth(self):
        return self.longitude < -100 or self.longitude > 100 or self.latitude < -100 or self.latitude > 100

    def __str__(self):
        return f"Titanic ({'under' if self.sunk else 'in'} the ocean)"

    def __repr__(self):
        return super().__repr__() + f", sunk={self.sunk}))"

