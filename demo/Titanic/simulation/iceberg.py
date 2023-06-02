from simulation.floating_object import FloatingObject


class Iceberg(FloatingObject):
    def __init__(self, x, y):
        super().__init__(x, y, 0, 0)
