from FloatingObject import FloatingObject


class Iceberg(FloatingObject):
    def __init__(self, x, y, speed, direction):
        super().__init__(x, y, speed, direction)

    def update_position(self):
        # For now Icebergs are static
        pass
