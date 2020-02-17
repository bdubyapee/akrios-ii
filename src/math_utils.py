#! usr/bin/env python
# Project: Akrios
# Filename: math.py
# 
# File Description: Math functions that may be handy to have available.
# 
# By: Jubelo

import random
from functools import reduce


def dice(num, sides, bonus=0):
    def accumulate(x, s=sides):
        return x + random.randrange(s)
    
    roll = reduce(accumulate, list(list(range(num+1)))) + num

    return roll + bonus


def fuzz(x, y, z):
    return random.randint(x, y) + z
