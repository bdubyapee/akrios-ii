#! usr/bin/env python
# Project: Akrios
# Filename: affects.py
# 
# File Description: Tables and functions related to affects
#
# By: Jubelo

from collections import namedtuple


Affect = namedtuple("Affect", "name")

affects = {"blind", Affect("blind"),
           "curse", Affect("curse"),
           "charm", Affect("charm"),
           "invisible", Affect("invisible"),
           "detect evil", Affect("detect evil"),
           "detect invisibility", Affect("detect invisibility"),
           "detect magic", Affect("detect magic"),
           "detect hidden", Affect("detect hidden"),
           "detect good", Affect("detect good"),
           "sanctuary", Affect("sanctuary"),
           "faerie fire", Affect("faerie fire"),
           "infrared", Affect("infrared"),
           "poison", Affect("poison"),
           "protection from evil", Affect("protection from evil"),
           "protection from good", Affect("protection from good"),
           "sneak", Affect("sneak"),
           "hide", Affect("hide"),
           "sleep", Affect("sleep"),
           "flying", Affect("flying"),
           "pass door", Affect("pass door"),
           "haste", Affect("haste"),
           "calm", Affect("calm"),
           "plague", Affect("plague"),
           "weaken", Affect("weaken"),
           "dark vision", Affect("dark vision"),
           "berserk", Affect("berserk"),
           "slow", Affect("slow"),
           "stone skin", Affect("stone skin"),
           "stun", Affect("stun"),
           "clumsy", Affect("clumsy"),
           "focus", Affect("focus"),
           "mute", Affect("mute"),
           "true sight", Affect("true sight"),
           "deaf", Affect("deaf"),
           "terror", Affect("terror"),
           "paralyzed", Affect("paralyzed"),
           "encumbered", Affect("encumbered"),
           "magic resistance", Affect("magic resistance"),
           "psionic resistance", Affect("psionic resistance"),
           "stat strength", Affect("stat strength"),
           "stat agility", Affect("stat agility"),
           "stat speed", Affect("stat speed"),
           "stat intelligence", Affect("stat intelligence"),
           "stat wisdom", Affect("stat wisdom"),
           "stat charisma", Affect("stat charisma"),
           "stat luck", Affect("stat luck"),
           "stat constitution", Affect("stat constitution")}


class OneAffect(object):
    def __init__(self, name, duration=0, value=0):
        if name not in affects:
            raise Exception("Creating affect not in list")

        self.name = ""
        self.duration = duration
        self.value = value
