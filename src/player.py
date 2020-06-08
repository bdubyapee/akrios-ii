#! usr/bin/env python
# Project: Akrios
# Filename: player.py
# 
# File Description: The player module.
# 
# By: Jubelo

import logging
import json
import os

import area
import livingthing
import objects
import races

log = logging.getLogger(__name__)

WRITE_NEW_FILE_VERSION = False

playerlist = []
playerlist_by_name = {}
playerlist_by_aid = {}


class Player(livingthing.LivingThing):
    CLASS_NAME = "__Player__"
    FILE_VERSION = 1

    def __init__(self, path=None):
        super().__init__()
        self.filename = path
        self.json_version = Player.FILE_VERSION
        self.json_class_name = Player.CLASS_NAME
        self.capability = ['player']
        self.password = ''
        self.lasthost = ''
        self.lasttime = ''
        self.oocflags = {'afk': False,
                         'viewOLCdetails': False,
                         'coding': False,
                         'grapevine_channels': ['gossip'],
                         'is_paginating': False}
        self.oocflags_stored = {'newbie': 'true',
                                'grapevine': 'true',
                                'ooc': 'true',
                                'paginate': 'true',
                                'quote': 'true'}
        self.sock = None
        self.uuid = ''

    async def load(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r") as thefile:
                player_file_dict = json.loads(thefile.read())
                for eachkey, eachvalue in player_file_dict.items():
                    setattr(self, eachkey, eachvalue)

            log.debug(f"Loading player: {self.name}")

            if self.contents:
                self.contents = {k: objects.Object(None, v, load_type="inventory")
                                 for k, v in self.contents.items()}

            self.race = races.racebyname(self.race)

            if not self.equipped:
                self.equipped = {k: None for k in self.race.wearlocations}

            self.location = area.room_by_vnum_global(self.location)
            await self.move(self.location)

    def to_json(self):
        if self.json_version == 1:
            jsonable = self.to_json_base()
            player_json = {"json_version": self.json_version,
                           "json_class_name": self.json_class_name,
                           "location": self.location.vnum,
                           "password": self.password,
                           "lasthost": self.lasthost,
                           "lasttime": self.lasttime,
                           "oocflags_stored": self.oocflags_stored}

            jsonable.update(player_json)

            return json.dumps(jsonable, sort_keys=True, indent=4)

    def save(self):
        if self.json_version == 1:
            with open(f"{self.filename}", "w") as thefile:
                thefile.write(self.to_json())

    @property
    def is_building(self):
        return True if hasattr(self, "building") else False

    @property
    def is_editing(self):
        return True if hasattr(self, "editing") else False


# Communications functions below

async def wiznet(msg=""):
    msg = f"\n\r\n\r{{YWiznet: {msg.capitalize()[0]}{msg[1:]}{{x"
    log.info(msg.lstrip())
    for person in playerlist:
        if person.is_admin:
            await person.write(msg)
