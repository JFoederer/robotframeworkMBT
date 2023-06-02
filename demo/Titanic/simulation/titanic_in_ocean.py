from simulation.floating_object import FloatingObject
from system.titanic import Titanic


class TitanicInOcean(FloatingObject):
    def __new__(cls, titanic, n, w, speed, direction, sunk=False):
        if not hasattr(cls, "instance"):
            cls.instance = super(TitanicInOcean, cls).__new__(cls)
        return cls.instance

    def __init__(self, titanic, n, w, speed, direction, sunk=False):
        super().__init__(n, w, speed, direction)
        self.sunk = sunk
        self.titanic = titanic

    def __repr__(self):
        return super().__repr__() + " sunk={self.sunk}))"