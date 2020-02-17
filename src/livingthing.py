#! usr/bin/env python
# Project: Akrios
# Filename: livingthing.py
# 
# File Description: The livingthing module.  All living things inherit from this.
#                   This includes mobiles and players.
# 
# By: Jubelo

# Imports here
from collections import namedtuple
import logging

import atomic

log = logging.getLogger(__name__)

# Define named tuples for living things.

Position = namedtuple("Position", "name")

positions = {"dead": Position("dead"),
             "incapacitated": Position("incapacitated"),
             "sleeping": Position("sleeping"),
             "stunned": Position("stunned"),
             "laying": Position("laying"),
             "crawling": Position("crawling"),
             "sitting": Position("sitting"),
             "standing": Position("standing")}

Gender = namedtuple("Gender", "name")

genders = {"male": Gender("male"),
           "female": Gender("female"),
           "other": Gender("other")}

Discipline = namedtuple("Discipline", "name")

disciplines = {"physical": Discipline("physical"),
               "mental": Discipline("mental"),
               "mystic": Discipline("mystic"),
               "divine": Discipline("divine")}

StatType = namedtuple("StatType", "name")

stat_type_strength = StatType("strength")
stat_type_agility = StatType("agility")
stat_type_speed = StatType("speed")
stat_type_intelligence = StatType("intelligence")
stat_type_wisdom = StatType("wisdom")
stat_type_charisma = StatType("charisma")
stat_type_luck = StatType("luck")
stat_type_constitution = StatType("constitution")

stat_types = {"strength": stat_type_strength,
              "agility": stat_type_agility,
              "speed": stat_type_speed,
              "intelligence": stat_type_intelligence,
              "wisdom": stat_type_wisdom,
              "charisma": stat_type_charisma,
              "luck": stat_type_luck,
              "constitution": stat_type_constitution}


class LivingThing(atomic.Atomic):
    def __init__(self):
        super().__init__()
        self.name = ''
        self.lastname = ''
        self.long_description = ''
        self.short_description = ''
        self.gender = 'male'
        self.location = None
        self.contents = {}
        self.capability = []
        self.last_input = 0
        self.race = None
        self.skillpoints = 0
        self.skills_learned = {}
        self.skills_specialties = {}
        self.aid = ''
        self.age = 1
        self.level = 1
        self.alignment = 'neutral'
        self.exp = {'combat': 0,
                    'explore': 0,
                    'profession': 0}
        self.maximum_stat = {'strength': 1, 'agility': 1, 'speed': 1, 'intelligence': 1,
                             'wisdom': 1, 'charisma': 1, 'luck': 1, 'constitution': 1}
        self.current_stat = {'strength': 1, 'agility': 1, 'speed': 1, 'intelligence': 1,
                             'wisdom': 1, 'charisma': 1, 'luck': 1, 'constitution': 1}
        self.money = {'copper': 0,
                      'silver': 0,
                      'gold': 0,
                      'platinum': 0}
        self.height = {'feet': 5,
                       'inches': 1}
        self.weight = 1
        self.hunger = 0
        self.thirst = 0
        self.wimpy = 0
        self.maxhp = 1
        self.currenthp = 1
        self.maxmovement = 1
        self.currentmovement = 1
        self.maxwillpower = 0
        self.currentwillpower = 0
        self.hitroll = 0
        self.damroll = 0
        self.totalmemoryslots = {'first circle': 0,
                                 'second circle': 0,
                                 'third circle': 0,
                                 'fourth circle': 0,
                                 'fifth circle': 0,
                                 'sixth circle': 0,
                                 'seventh circle': 0,
                                 'eighth circle': 0,
                                 'ninth circle': 0}
        self.memorizedspells = {}
        self.spells_learned = {}
        self.runes_imprinted = {}
        self.psionic_abilities = {}
        self.guild = None
        self.council = None
        self.family = None
        self.clan = None
        self.deity = ''
        self.discipline = None
        self.equipped = {}
        self.baceac = {'slashing': 0,
                       'piercing': 0,
                       'bashing': 0,
                       'lashing': 0}
        self.currentac = {'slashing': 0,
                          'piercing': 0,
                          'bashing': 0,
                          'lashing': 0}
        self.position = None
        self.title = ''
        self.seen_as = ''
        self.prompt = ''
        self.knownpeople = {}
        self.alias = {}
        self.snooped_by = []

    def to_json_base(self):
        jsonable = {"name": self.name,
                    "lastname": self.lastname,
                    "capability": self.capability,
                    "long_description": self.long_description,
                    "short_description": self.short_description,
                    "race": self.race.name,
                    "age": self.age,
                    "gender": self.gender,
                    "level": self.level,
                    "alignment": self.alignment,
                    "money": self.money,
                    "height": self.height,
                    "weight": self.weight,
                    "maxhp": self.maxhp,
                    "currenthp": self.currenthp,
                    "maxmovement": self.maxmovement,
                    "currentmovement": self.currentmovement,
                    "maxwillpower": self.maxwillpower,
                    "currentwillpower": self.currentwillpower,
                    "totalmemoryslots": self.totalmemoryslots,
                    "memorizedspells": self.memorizedspells,
                    "spells_learned": self.spells_learned,
                    "runes_imprinted": self.runes_imprinted,
                    "psionic_abilities": self.psionic_abilities,
                    "hitroll": self.hitroll,
                    "damroll": self.damroll,
                    "wimpy": self.wimpy,
                    "title": self.title,
                    "guild": self.guild,
                    "council": self.council,
                    "family": self.family,
                    "clan": self.clan,
                    "deity": self.deity,
                    "skillpoints": self.skillpoints,
                    "skills_learned": self.skills_learned,
                    "skills_specialties": self.skills_specialties,
                    "seen_as": self.seen_as,
                    "maximum_stat": self.maximum_stat,
                    "current_stat": self.current_stat,
                    "discipline": self.discipline,
                    "exp": self.exp,
                    "equipped": self.equipped,
                    "baceac": self.baceac,
                    "currentac": self.currentac,
                    "hunger": self.hunger,
                    "thirst": self.thirst,
                    "position": self.position,
                    "aid": self.aid,
                    "knownpeople": self.knownpeople,
                    "prompt": self.prompt,
                    "alias": self.alias}

        if self.contents:
            jsonable["contents"] = {k: v.to_json() for k, v in self.contents.items()}

        return jsonable

    def add_known(self, idnum=None, name=None):
        if idnum is None or name is None:
            log.warning("You must provide id and name arguments to add_known")
        else:
            self.knownpeople[idnum] = name

    def get_known(self, idnum=None):
        if idnum is None:
            log.warning("You must provide an idnum to get_known")
            return

        return self.knownpeople[idnum] if idnum in self.knownpeople else ''
