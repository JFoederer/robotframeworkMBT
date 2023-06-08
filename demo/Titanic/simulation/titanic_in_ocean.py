from __future__ import annotations

from simulation.floating_object import FloatingObject


class TitanicInOcean(FloatingObject):

    instance: TitanicInOcean = None

    def __new__(cls, titanic, n, w, speed, direction, sunk=False):
        if not cls.instance:
            cls.instance = super(TitanicInOcean, cls).__new__(cls)
        return cls.instance

    def __init__(self, titanic, n, w, speed, direction):
        super().__init__(n, w, speed, direction)
        self.sunk = False
        self.titanic = titanic

    def collided(self):
        """
        Emulate what happens when Titanic hits another object in the sea.
        Loses all speed, sets titanic's damage flag to True and sets the sunk flag to True
        """
        self.speed = 0

        self.titanic.damaged = True
        # TODO First the titanic will take damage. As time passes it will sink.
        self.sunk = True

    def __str__(self):
        return f"Titanic ({'under' if self.sunk else 'in'} the ocean)"

    def __repr__(self):
        return super().__repr__() + f", sunk={self.sunk}))"

