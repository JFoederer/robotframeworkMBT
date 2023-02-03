#!/usr/bin/env python3

from enum import Enum

class Emotion(Enum):
    HAPPY = 1
    SHOCKED = 2
    RELIEVED = 3    

class People(object):
    
    def __init__(self):
        self.emotion = Emotion.HAPPY

