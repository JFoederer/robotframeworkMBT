from FloatingObject import FloatingObject


class Titanic(FloatingObject):
    def __new__(cls, x, y, speed, direction):
        if not hasattr(cls, "instance"):
            cls.instance = super(Titanic, cls).__new__(cls)
        return cls.instance

    def __init__(self, x, y, speed, direction):
        super().__init__(x, y, speed, direction)
        self.throttle = speed
        self.steering_direction = direction
        self.damaged = False

    def __repr__(self):
        return f"{type(self).__name__} (throttle={self.throttle}, steering_direction={self.steering_direction}, position={self.position.items()}, damaged={self.damaged})"
