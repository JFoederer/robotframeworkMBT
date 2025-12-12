
class Titanic:

    def __init__(self, throttle, steering_direction):
        self.throttle = throttle  # percentage
        # degrees (0 means steering straight)
        self.steering_direction = steering_direction
        self.damaged = False

    def __repr__(self):
        return f"{type(self).__name__} (throttle={self.throttle}, steering_direction={self.steering_direction}, damaged={self.damaged})"
