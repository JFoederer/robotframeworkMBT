from FloatingObject import FloatingObject
from Titanic import Titanic
from Iceberg import Iceberg
from TitanicInOcean import TitanicInOcean
from Journey import Journey
from Ocean import Ocean


def main():
    t = Titanic(6, 7, 9, "west")
    tio = TitanicInOcean(t)
    iceberg = Iceberg(7, 7, 9, "south")
    ocean = Ocean()
    ocean.floating_objects.append(t)
    ocean.floating_objects.append(iceberg)
    j = Journey(t, ocean)
    print(t.distance_to(iceberg))
    print(t)
    print(tio)
    print(j)
    print(ocean.floating_objects)
    print("__________________________")
    j.passed_time(10)


if __name__ == "__main__":
    main()