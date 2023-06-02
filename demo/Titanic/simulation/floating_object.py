import math


class FloatingObject:
    def __init__(self, n, w, speed, direction):
        self.speed = speed
        self.direction = direction
        self.position = {"n": n, "w": w}

    def __repr__(self):
        return f"{type(self).__name__} (speed={self.speed}, direction={self.direction}, position={self.position.items()})"

    def distance_to(self, floating_object):
        return round(
            math.sqrt(
                ((self.position["n"] - floating_object.position["n"]) ** 2)
                + ((self.position["w"] - floating_object.position["w"]) ** 2)
            ),
            2,
        )

    def update_position(self):
        if self.direction == "south":
            self.position["w"] = self.position["w"] - 1
        elif self.direction == "north":
            self.position["w"] = self.position["w"] + 1
        elif self.direction == "west":
            self.position["n"] = self.position["n"] - 1
        elif self.direction == "east":
            self.position["n"] = self.position["n"] + 1
