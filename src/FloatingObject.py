import math


class FloatingObject:
    def __init__(self, x, y, speed, direction):
        self.speed = speed
        self.direction = direction
        self.position = {"x": x, "y": y}

    def __repr__(self):
        return f"{type(self).__name__} (speed={self.speed}, direction={self.direction}, position={self.position.items()})"

    def distance_to(self, floating_object):
        return round(
            math.sqrt(
                ((self.position["x"] - floating_object.position["x"]) ** 2)
                + ((self.position["y"] - floating_object.position["y"]) ** 2)
            ),
            2,
        )

    def update_position(self):
        if self.direction == "south":
            self.position["y"] = self.position["y"] - 1
        elif self.direction == "north":
            self.position["y"] = self.position["y"] + 1
        elif self.direction == "west":
            self.position["x"] = self.position["x"] - 1
        elif self.direction == "east":
            self.position["x"] = self.position["x"] + 1
