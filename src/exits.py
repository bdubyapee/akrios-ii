#! usr/bin/env python
# Project: Akrios
# Filename: exits.py
# 
# File Description: Module dealing with exits specifically.
# 
# By: Jubelo

from collections import namedtuple
import json
import logging

import olc

log = logging.getLogger(__name__)

# Define some tuples here for standard directions.
directions = ('north', 'south', 'east', 'west', 'northwest', 'northeast',
              'southwest', 'southeast', 'up', 'down')

oppositedirection = {'north': 'south',
                     'south': 'north',
                     'east': 'west',
                     'west': 'east',
                     'northwest': 'southeast',
                     'northeast': 'southwest',
                     'southwest': 'northeast',
                     'southeast': 'northwest',
                     'up': 'down',
                     'down': 'up'}

# Define named tuples for exits as a full blown class may be overkill for now.
Exit_Size = namedtuple('Exit_Sizes', 'name height width')

exit_size_vast = Exit_Size('vast', 1000, 1000)      # Vast, Wide Open
exit_size_huge = Exit_Size('huge', 240, 240)        # 20' x 20'
exit_size_large = Exit_Size('large', 120, 120)      # 10' x 10 '
exit_size_medium = Exit_Size('medium', 84, 84)      # 7' x 7'
exit_size_small = Exit_Size('small', 48, 48)        # 4' x 4'
exit_size_tiny = Exit_Size('tiny', 12, 12)          # 1' x 1'
exit_size_miniscule = Exit_Size('miniscule', 6, 6)  # 5" x 5"

exit_sizes = {'vast': exit_size_vast,
              'huge': exit_size_huge,
              'large': exit_size_large,
              'medium': exit_size_medium,
              'small': exit_size_small,
              'tiny': exit_size_tiny,
              'miniscule': exit_size_miniscule}


# Define any module constants here.

WRITE_NEW_FILE_VERSION = False


class Exit(olc.Editable):
    CLASS_NAME = "__Exit__"
    FILE_VERSION = 1

    def __init__(self, room, direction_fn=None, data=None):
        super().__init__()
        self.json_version = Exit.FILE_VERSION
        self.json_class_name = Exit.CLASS_NAME
        self.capability = ['exit']
        self.room = room
        if direction_fn is None:
            self.direction = ''
        else:
            self.direction = direction_fn
        self.destination = 0
        self.locked = 'false'
        self.lockdifficulty = 0
        self.keyvnum = 0
        self.magiclocked = 'false'
        self.physicaldifficulty = 0
        self.magiclockdifficulty = 0
        self.casterid = 0
        self.magiclocktype = 'none'
        self.size = 'vast'
        self.hasdoor = 'false'
        self.dooropen = 'true'
        self.keywords = []
        self.commands = {'direction': ('string', directions),
                         'destination': ('integer', None),
                         'locked': ('string', ['true', 'false']),
                         'lockdifficulty': ('integer', None),
                         'keyvnum': ('integer', None),
                         'magiclocked': ('string', ['true', 'false']),
                         'physicaldifficulty': ('integer', None),
                         'magiclockdifficulty': ('integer', None),
                         'casterid': ('integer', None),
                         'magiclocktype': ('string', None),
                         'size': ('string', exit_sizes),
                         'hasdoor': ('string', ['true', 'false']),
                         'dooropen': ('string', ['true', 'false']),
                         'keywords': ('list', None)}
        if data is not None:
            self.load(data)

    def to_json(self):
        if self.json_version == 1:
            jsonable = {"json_version": self.json_version,
                        "json_class_name": self.json_class_name,
                        "direction": self.direction,
                        "room": int(self.room.vnum),
                        "destination": self.destination,
                        "locked": self.locked,
                        "lockdifficulty": self.lockdifficulty,
                        "keyvnum": self.keyvnum,
                        "magiclocked": self.magiclocked,
                        "physicaldifficulty": self.physicaldifficulty,
                        "magiclockdifficulty": self.magiclockdifficulty,
                        "casterid": self.casterid,
                        "magiclocktype": self.magiclocktype,
                        "size": self.size,
                        "hasdoor": self.hasdoor,
                        "dooropen": self.dooropen,
                        "keywords": self.keywords}
            return json.dumps(jsonable, sort_keys=True, indent=4)

    def load(self, data):
        log.debug(f"Loading exit({self.direction}) in room: {self.room}[{self.room.vnum}]")
        for eachkey, eachvalue in json.loads(data).items():
            if eachkey != "room":
                setattr(self, eachkey, eachvalue)

        self.room.exits[self.direction] = self

    def display(self):
        return (f"{{BRoom{{x: {self.room.name}\n"
                f"{{BDirection{{x: {self.direction}\n"
                f"{{BDestination{{x: {self.destination}\n"
                f"{{BLocked{{x: {self.locked}\n"
                f"{{BLock Difficulty{{x: {self.lockdifficulty}\n"
                f"{{BKey Vnum{{x: {self.keyvnum}\n"
                f"{{BMagic Locked{{x: {self.magiclocked}\n"
                f"{{BPhysical Difficulty{{x: {self.physicaldifficulty}\n"
                f"{{BMagic Lock Difficulty{{x: {self.magiclockdifficulty}\n"
                f"{{BCaster ID{{x: {self.casterid}\n"
                f"{{BMagic Lock Type{{x: {self.magiclocktype}\n"
                f"{{BSize{{x: {self.size}\n"
                f"{{BHas Door{{x: {self.hasdoor}\n"
                f"{{BDoor Open{{x: {self.dooropen}\n"
                f"{{BKeywords{{x: {', '.join(self.keywords)}\n")
