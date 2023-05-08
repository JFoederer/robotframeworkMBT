from FloatingObject import FloatingObject
from Titanic import Titanic


class TitanicInOcean(FloatingObject):
    def __new__(cls, titanic, sunk=False):
        if not hasattr(cls, "instance"):
            cls.instance = super(TitanicInOcean, cls).__new__(cls)
        return cls.instance

    def __init__(self, titanic, sunk=False):
        self.sunk = sunk
        self.titanic = titanic

    def __repr__(self):
        return f"{type(self).__name__}, ({self.titanic.__class__.__name__} (speed={self.titanic.speed}, direction={self.titanic.direction}, position={self.titanic.position}, sunk={self.sunk}))"
