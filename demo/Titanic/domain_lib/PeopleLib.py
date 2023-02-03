#!/usr/bin/env python3


from enum import Enum

from system.People import People, Emotion

class PeopleLib(object):
    
    def __init__(self):
        self.people = People()

    def the_people_are_shocked(self):

        print("The people: WOW we are so shocked!!")

        self.people.emotion = Emotion.SHOCKED


