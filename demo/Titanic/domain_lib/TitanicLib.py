#!/usr/bin/env python3

from system.Titanic import Titanic

class TitanicLib(object):

    def __init__(self):
        self.titanic = Titanic()
    
    def hits_a_huge_iceberg(self):

        print("Hit a huge iceberg!")

        self.titanic.is_sinking = True