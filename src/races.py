#! usr/bin/env python
# Project: Akrios
# Filename: races.py
# 
# File Description: Module to deal with races.
# 
# By: Jubelo

import glob
import logging
import os
import json

import olc
import world

log = logging.getLogger(__name__)

WRITE_NEW_FILE_VERSION = False

sizelist = ('tiny', 'small', 'medium', 'large', 'huge')

alignment = ('lawful good', 'lawful neutral', 'lawful evil',
             'neutral good', 'neutral', 'neutral evil',
             'chaotic good', 'chaotic neutral', 'chaotic evil')

bodypartslist = ('head', 'face', 'hand', 'leg', 'foot', 'nose', 'ear', 'scalp', 'torso', 'finger',
                 'toe', 'entrails', 'wing', 'tail', 'snout', 'shell', 'antenna', 'paw',
                 'fin', 'scale', 'rattle', 'tongue', 'eye', 'skull', 'arm', 'bone', 'pelt', 'heart',
                 'liver', 'stomach', 'kidney', 'lung', 'gills', 'claw', 'beak', 'feather',
                 'whisker', 'tooth', 'tusk', 'horn', 'hoof', 'hide', 'tentacle', 'mane', 'mandible',
                 'thorax')

wearlocationslist = ('head', 'face', 'eyes', 'neck', 'left arm', 'right arm',
                     'right forearm', 'left forearm', 'finger', 'left hand',
                     'right hand', 'torso', 'back', 'waist', 'left leg',
                     'right leg', 'left shin', 'right shin', 'left foot',
                     'right foot', 'legs', 'feet', 'left shoulder', 'right shoulder',
                     'upper right arm', 'upper left arm',
                     'upper right hand', 'upper left hand', 'upper right forearm',
                     'upper left forearm', 'horns', 'floating nearby', 'tail')

height_list_values = [number for number in range(12)]
ac_and_resistance_values = [number for number in range(-50, 51)]
start_locationlist = {'drowhome': 101, 'stormhaven': 101, 'whitestone keep': 101}
special_skillslist = ['drow', 'elven', 'high elven', 'common']


class Race(olc.Editable):
    CLASS_NAME = "__Race__"
    FILE_VERSION = 1

    def __init__(self, path):
        super().__init__()
        self.path = path
        self.json_version = Race.FILE_VERSION
        self.json_class_name = Race.CLASS_NAME
        self.builder = None
        self.name = ''
        self.description = ''
        self.alignment = []
        self.playable = 'false'
        self.descriptive = ''
        self.size = ''
        self.heightfeet = 0
        self.heightinches = 0
        self.undead = 'false'
        self.weight = 0
        self.ageminimum = 0
        self.agemaximum = 0
        self.ba_slashing = 0
        self.ba_bashing = 0
        self.ba_piercing = 0
        self.ba_lashing = 0
        self.br_fire = 0
        self.br_ice = 0
        self.br_lightning = 0
        self.br_earth = 0
        self.br_disease = 0
        self.br_poison = 0
        self.br_magic = 0
        self.br_holy = 0
        self.br_mental = 0
        self.br_physical = 0
        self.wearlocations = []
        self.bodyparts = []
        self.skin = []
        self.eyes = []
        self.hair = []
        self.speed = 0
        self.agility = 0
        self.strength = 0
        self.intelligence = 0
        self.wisdom = 0
        self.charisma = 0
        self.luck = 0
        self.constitution = 0
        self.start_location = {}
        self.special_skills = {}
        self.commands = {'name': ('string', None),
                         'description': ('description', None),
                         'alignment': ('list', alignment),
                         'playable': ('string', ['true', 'false']),
                         'descriptive': ('string', None),
                         'size': ('string', sizelist),
                         'heightfeet': ('integer', height_list_values),
                         'heightinches': ('integer', height_list_values),
                         'undead': ('string', ['true', 'false']),
                         'weight': ('integer', None),
                         'ageminimum': ('integer', None),
                         'agemaximum': ('integer', None),
                         'ba_slashing': ('integer', ac_and_resistance_values),
                         'ba_bashing': ('integer', ac_and_resistance_values),
                         'ba_piercing': ('integer', ac_and_resistance_values),
                         'ba_lashing': ('integer', ac_and_resistance_values),
                         'br_fire': ('integer', ac_and_resistance_values),
                         'br_ice': ('integer', ac_and_resistance_values),
                         'br_lightning': ('integer', ac_and_resistance_values),
                         'br_earth': ('integer', ac_and_resistance_values),
                         'br_disease': ('integer', ac_and_resistance_values),
                         'br_poison': ('integer', ac_and_resistance_values),
                         'br_magic': ('integer', ac_and_resistance_values),
                         'br_holy': ('integer', ac_and_resistance_values),
                         'br_mental': ('integer', ac_and_resistance_values),
                         'br_physical': ('integer', ac_and_resistance_values),
                         'wearlocations': ('list', wearlocationslist),
                         'bodyparts': ('list', bodypartslist),
                         'skin': ('list', None),
                         'eyes': ('list', None),
                         'hair': ('list', None),
                         'speed': ('integer', None),
                         'agility': ('integer', None),
                         'strength': ('integer', None),
                         'intelligence': ('integer', None),
                         'wisdom': ('integer', None),
                         'charisma': ('integer', None),
                         'luck': ('integer', None),
                         'constitution': ('integer', None),
                         'start_location': ('dict', (list(start_locationlist.keys()),
                                                     list(start_locationlist.values()))),
                         'special_skills': ('list', special_skillslist)}
        if os.path.exists(path):
            self.load()

    def load(self):
        with open(self.path, "r") as thefile:
            race_file_dict = json.loads(thefile.read())
            for eachkey, eachvalue in race_file_dict.items():
                setattr(self, eachkey, eachvalue)
        log.debug(f"Loading race: {self.name}")

    def to_json(self):
        if self.json_version == 1:
            jsonable = {'json_version': self.json_version,
                        'json_class_name': self.json_class_name,
                        'name': self.name,
                        'description': self.description,
                        'alignment': self.alignment,
                        'playable': self.playable,
                        'descriptive': self.descriptive,
                        'size': self.size,
                        'heightfeet': self.heightfeet,
                        'heightinches': self.heightinches,
                        'undead': self.undead,
                        'weight': self.weight,
                        'ageminimum': self.ageminimum,
                        'agemaximum': self.agemaximum,
                        'ba_slashing': self.ba_slashing,
                        'ba_bashing': self.ba_bashing,
                        'ba_piercing': self.ba_piercing,
                        'ba_lashing': self.ba_lashing,
                        'br_fire': self.br_fire,
                        'br_ice': self.br_ice,
                        'br_lightning': self.br_lightning,
                        'br_earth': self.br_earth,
                        'br_disease': self.br_disease,
                        'br_poison': self.br_poison,
                        'br_magic': self.br_magic,
                        'br_holy': self.br_holy,
                        'br_mental': self.br_mental,
                        'br_physical': self.br_physical,
                        'wearlocations': self.wearlocations,
                        'bodyparts': self.bodyparts,
                        'skin': self.skin,
                        'eyes': self.eyes,
                        'hair': self.hair,
                        'speed': self.speed,
                        'agility': self.agility,
                        'strength': self.strength,
                        'intelligence': self.intelligence,
                        'wisdom': self.wisdom,
                        'charisma': self.charisma,
                        'luck': self.luck,
                        'constitution': self.constitution,
                        'start_location': self.start_location,
                        'special_skills': self.special_skills}
            return json.dumps(jsonable, sort_keys=True, indent=4)

    def save(self):
        if self.json_version == 1:
            with open(f"{self.path}", "w") as thefile:
                thefile.write(self.to_json())

    def display(self):
        return (
            f"{{BName{{x: {self.name.capitalize():15}  {{BAlignment{{x: {' '.join(self.alignment):15}  {{BPlayable{{x: {self.playable:15}\n\r"
            f"{{BDescriptive{{x: {self.descriptive:70}\n\r"
            f"{{BSize{{x: {self.size:10}  {{BHeightFeet{{x: {self.heightfeet:<2}   {{BHeightInches{{x: {self.heightinches:<2}\n\r"
            f"{{BUndead{{x: {self.undead:11}   {{BWeight{{x: {self.weight:<5}  {{BAgeMinimum{{x: {self.ageminimum:<4}  {{BAgeMaximum{{x: {self.agemaximum:<4}\n\r"
            f"\n\r"
            f"{{BSpeed{{x: {self.speed:4}  {{BAgility{{x: {self.agility:3} {{BStrength{{x: {self.strength:3} {{BIntelligence{{x: {self.intelligence:3}\n\r"
            f"{{BWisdom{{x: {self.wisdom:3} {{BCharisma{{x: {self.charisma:3} {{BLuck{{x: {self.luck:7} {{BConstitution{{x: {self.constitution:3}\n\r"
            f"\n\r"
            f"\n\r"
            f"{{BBr_Fire{{x: {self.br_fire:8}     {{BBr_Ice{{x: {self.br_ice:8}     {{BBa_Slashing{{x: {self.ba_slashing:3}\n\r"
            f"{{BBr_Lightning{{x: {self.br_lightning:3}     {{BBr_Earth{{x: {self.br_earth:6}     {{BBa_Bashing{{x: {self.ba_bashing:4}\n\r"
            f"{{BBr_Disease{{x: {self.br_disease:5}     {{BBr_Poison{{x: {self.br_poison:5}     {{BBa_Piercing{{x: {self.ba_piercing:3}\n\r"
            f"{{BBr_Magic{{x: {self.br_magic:7}     {{BBr_Holy{{x: {self.br_holy:7}     {{BBa_Lashing{{x: {self.ba_lashing:4}\n\r"
            f"{{BBr_Mental{{x: {self.br_mental:6}     {{BBr_Physical{{x: {self.br_physical:3}\n\r"
            f"\n\r"
            f"{{BSkin{{x: {', '.join(self.skin):35} {{BEyes{{x: {', '.join(self.eyes):35}\n\r"
            f"{{BHair{{x: {', '.join(self.hair):60}\n\r"
            f"{{BWearLocations{{x: {', '.join(self.wearlocations)}\n\r"
            f"{{BBodyParts{{x:\n\r {', '.join(self.bodyparts)}\n\r"
            f"{{BStart_Location{{x: {self.start_location}\n\r"
            f"{{BSpecial_Skills{{x: {self.special_skills}\n\r"
            f"{{BDescription{{x:\n\r"
            f"{self.description[:180]}...\n\r{{x")


goodraces = []
neutralraces = []
evilraces = []
racesdict = {}


def init():
    log.info("Initializing races")
    racepaths = glob.glob(os.path.join(world.raceDir, '*.json'))
    for racepath in racepaths:
        therace = Race(racepath)
        addtolist(therace)
        if WRITE_NEW_FILE_VERSION:
            therace.save()


def reload():
    racesdict.clear()
    goodraces.clear()
    neutralraces.clear()
    evilraces.clear()
    init()


def addtolist(race):
    racesdict[race.name.lower()] = race
    alignments = {'lawful good': goodraces,
                  'neutral good': goodraces,
                  'chaotic good': goodraces,
                  'lawful neutral': neutralraces,
                  'neutral': neutralraces,
                  'chaotic neutral': neutralraces,
                  'lawful evil': evilraces,
                  'neutral evil': evilraces,
                  'chaotic evil': evilraces}
    if race.alignment[0].lower() in alignments and race.playable == 'true':
        alignments[race.alignment[0]].append(race.name.lower())


def racebyname(name):
    if name in racesdict:
        return racesdict[name]
    else:
        raise SyntaxError("That's not a race I recognize.")


def race_names_by_alignment(alignment_="good"):
    if alignment_ == "good":
        return ', '.join(goodraces)
    elif alignment_ == "neutral":
        return ', '.join(neutralraces)
    elif alignment_ == "evil":
        return ', '.join(evilraces)
    else:
        raise SyntaxError("races.py That is not an alignment I recognize.")
