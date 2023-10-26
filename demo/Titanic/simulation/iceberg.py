from simulation.floating_object import FloatingObject


class Iceberg(FloatingObject):

    def __init__(self, longitude, latitude):
        super().__init__(longitude, latitude, 0, 0)

    def __str__(self):
        return f"Some iceberg at {self.longitude}, {self.latitude}"

    def collided(self):
        print(f"Something hit {self}!")
