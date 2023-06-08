#!/usr/bin/env python3
from robot.api.deco import keyword

from simulation.titanic_in_ocean import TitanicInOcean


class TitanicLib:

    @keyword("Titanic is sinking")
    def titanic_is_sinking(self):
        return TitanicInOcean.instance.sunk

