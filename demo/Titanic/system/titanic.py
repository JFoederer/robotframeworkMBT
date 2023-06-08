
class Titanic:
    instance = None

    def __new__(cls, throttle, steering_direction):
        if not cls.instance:
            cls.instance = super(Titanic, cls).__new__(cls)
        return cls.instance

    def __init__(self, throttle, steering_direction):
        self.throttle = throttle
        self.steering_direction = steering_direction
        self.damaged = False

    def __repr__(self):
        return f"{type(self).__name__} (throttle={self.throttle}, steering_direction={self.steering_direction}, damaged={self.damaged})"
