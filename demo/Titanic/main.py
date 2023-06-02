from simulation.floating_object import FloatingObject
from system.titanic import Titanic
from simulation.iceberg import Iceberg
from simulation.titanic_in_ocean import TitanicInOcean
from simulation.journey import Journey
from simulation.ocean import Ocean


def main():
    t = Titanic(9, "east")
    tio = TitanicInOcean(t, 7,8,9, "west")
    iceberg = Iceberg(7, 7)
    ocean = Ocean()
    ocean.floating_objects.append(tio)
    ocean.floating_objects.append(iceberg)
    j = Journey(tio, ocean)
    print(tio.distance_to(iceberg))
    print("__________________________")
    j.passed_time(10)


if __name__ == "__main__":
    main()
