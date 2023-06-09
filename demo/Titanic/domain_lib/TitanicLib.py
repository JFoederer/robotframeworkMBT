#!/usr/bin/env python3
from robot.api.deco import keyword

from simulation.titanic_in_ocean import TitanicInOcean


class TitanicLib:

    @keyword("Titanic is sinking")
    def titanic_is_sinking(self):
        """
        Reports whether the titanic is sinking or not.
        @return: bool indicating sunk status of the Titanic in the ocean.
        """
        return TitanicInOcean.instance.sunk

