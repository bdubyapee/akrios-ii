#! usr/bin/env python
# Project: Akrios
# Filename: area.py
# 
# File Description: File dealing with areas
# 
# By: Jubelo

from collections import namedtuple
import logging
import os
import json
import glob

import exits
import mobile
import objects
import olc
import reset
import room
import world

log = logging.getLogger(__name__)

arealist = []

# Define some named tuples of various Area values.
Plane = namedtuple("Planes", "name")

planes = {"material": Plane("material"),
          "ethereal": Plane("ethereal")}


Difficulty = namedtuple("Difficulty", "name")

difficulty = {"all": Difficulty("all"),
              "very easy": Difficulty("very easy"),
              "easy": Difficulty("easy"),
              "moderate": Difficulty("moderate"),
              "hard": Difficulty("hard"),
              "very hard": Difficulty("very hard"),
              "extreme": Difficulty("extreme")}


async def init():
    log.info("Executing init()")
    for each_area_directory in glob.glob(os.path.join(world.areaDir, '*')):
        thefile = glob.glob(os.path.join(each_area_directory, '*.json'))
        thearea = Area(each_area_directory, thefile[0])
        await thearea.load()


def room_by_vnum_global(vnum):
    for each_area in arealist:
        if vnum in each_area.roomlist:
            return each_area.roomlist[vnum]


class Area(olc.Editable):
    CLASS_NAME = "__Area__"
    FILE_VERSION = 1

    def __init__(self, fpath, path):
        super().__init__()

        self.json_version = Area.FILE_VERSION
        self.json_class_name = Area.CLASS_NAME
        self.folder_path = fpath
        self.area_path = path
        self.name = ''
        self.author = ''
        self.plane = ''
        self.hometown = ''
        self.difficulty = ''
        self.alignment = ''
        self.locationx = 0
        self.locationy = 0
        self.vnumlow = -1
        self.vnumhigh = -1
        self.roomlist = {}
        self.mobilelist = []
        self.mobilelist_index = []
        self.mobilelist_by_vnum = {}
        self.mobilelist_by_vnum_index = {}
        self.objectlist = []
        self.objectlist_index = []
        self.objectlist_by_vnum_index = {}
        self.resetlist = None
        self.playerlist = []
        self.commands = {'name': ('string', None),
                         'author': ('string', None),
                         'plane': ('string', planes),
                         'hometown': ('string', None),
                         'difficulty': ('string', difficulty),
                         'alignment': ('string', None),
                         'locationx': ('integer', None),
                         'locationy': ('integer', None),
                         'vnumlow': ('integer', None),
                         'vnumhigh': ('integer', None)}

    def room_by_vnum(self, vnum):
        return self.roomlist[vnum] if vnum in self.roomlist else None

    def mobile_inst_by_vnum(self, vnum):
        for eachmob in self.mobilelist:
            if eachmob.vnum == vnum:
                return eachmob
        return False

    def object_inst_by_vnum(self, vnum):
        for eachobj in self.objectlist:
            if eachobj.vnum == vnum:
                return eachobj
        return False

    def to_json(self):
        if self.json_version == 1:
            jsonable = {"json_version": self.json_version,
                        "json_class_name": self.json_class_name,
                        "name": self.name,
                        "author": self.author,
                        "plane": self.plane,
                        "hometown": self.hometown,
                        "difficulty": self.difficulty,
                        "alignment": self.alignment,
                        "locationx": self.locationx,
                        "locationy": self.locationy,
                        "vnumlow": self.vnumlow,
                        "vnumhigh": self.vnumhigh}
            return json.dumps(jsonable, sort_keys=True, indent=4)

    @staticmethod
    def save():
        # Write new JSON formatted Exits for the area.
        for eacharea in arealist:
            exits_path = os.path.join(eacharea.folder_path, "exits")
            if not os.path.exists(exits_path):
                os.makedirs(exits_path)
            for eachroom in eacharea.roomlist:
                theroom = eacharea.room_by_vnum(eachroom)
                for eachexit in theroom.exits:
                    theexit = eacharea.roomlist[eachroom].exits[eachexit]
                    filename = os.path.join(eacharea.folder_path, f"exits/{eachroom}-{eachexit}.json")
                    with open(filename, 'w') as thefile:
                        thefile.write(theexit.to_json())

        # Write new JSON formatted Rooms for the area.
        for eacharea in arealist:
            rooms_path = os.path.join(eacharea.folder_path, "rooms")
            if not os.path.exists(rooms_path):
                os.makedirs(rooms_path)
            for eachroom in eacharea.roomlist:
                theroom = eacharea.room_by_vnum(eachroom)
                filename = os.path.join(eacharea.folder_path, f"rooms/{eachroom}.json")
                with open(filename, 'w') as thefile:
                    thefile.write(theroom.to_json())

        # Write new JSON formatted Mobiles for the area.
        for eacharea in arealist:
            mobiles_path = os.path.join(eacharea.folder_path, "mobiles")
            if not os.path.exists(mobiles_path):
                os.makedirs(mobiles_path)
            for mobile_vnum, mobile_ in eacharea.mobilelist_by_vnum_index.items():
                filename = os.path.join(eacharea.folder_path, f"mobiles/{mobile_vnum}.json")
                with open(filename, 'w') as thefile:
                    thefile.write(mobile_.to_json())

        # Write new JSON formatted Objects for the area.
        for eacharea in arealist:
            objects_path = os.path.join(eacharea.folder_path, "objects")
            if not os.path.exists(objects_path):
                os.makedirs(objects_path)
            for object_vnum, object_ in eacharea.objectlist_by_vnum_index.items():
                filename = os.path.join(eacharea.folder_path, f"objects/{object_vnum}.json")
                with open(filename, 'w') as thefile:
                    thefile.write(object_.to_json())

        # Write new JSON formatted reset information for the area.
        for eacharea in arealist:
            if eacharea.resetlist is None:
                continue

            resets_path = os.path.join(eacharea.folder_path, "resets")
            if not os.path.exists(resets_path):
                os.makedirs(resets_path)
            filename = os.path.join(eacharea.folder_path, f"resets/resets.json")
            with open(filename, 'w') as thefile:
                thefile.write(eacharea.resetlist.to_json())

        # Write new JSON formatted Area header for the area.
        for eacharea in arealist:
            filename = os.path.join(eacharea.folder_path, f"{eacharea.name}.json")
            with open(filename, 'w') as thefile:
                thefile.write(eacharea.to_json())

    async def load(self):
        log.info(f"Loading area: {self.area_path}")
        with open(self.area_path, 'r') as thefile:
            data = thefile.read()
        
        # Load Header Data into this Area
        log.info(f"Loading area Header: {self.area_path}")
        for eachkey, eachvalue in json.loads(data).items():
            setattr(self, eachkey, eachvalue)

        # Load each Room into this Area
        log.info(f"{self.name} : Loading area Rooms")
        roomfilepath = os.path.join(self.folder_path, f"rooms/*.json")
        filenames = glob.glob(roomfilepath)
        for eachfile in filenames:
            with open(eachfile, 'r') as thefile:
                room.Room(self, thefile.read())
 
        # Load each Exit and attach it to a room
        log.info(f"{self.name} : Loading area Exits")
        exitfilepath = os.path.join(self.folder_path, f"exits/*.json")
        filenames = glob.glob(exitfilepath)
        for eachfile in filenames:
            with open(eachfile, 'r') as thefile:
                # fullpath, direction_fn = eachfile.split('.')[0].split('-')
                # roomvnum = fullpath.split('/')[-1:][0]
                roomvnum, direction_fn = eachfile.split('.')[0].split('/')[-1].split('-')
                attached_room = self.room_by_vnum(int(roomvnum))
                if attached_room is None:
                    log.warning(f"room_by_vnum_global failed in exit load: {roomvnum}")
                else:
                    exits.Exit(attached_room, direction_fn, thefile.read())

        # Load each Mobile in to the Indexes.
        log.info(f"{self.name} : Loading area Mobiles")
        mobilefilepath = os.path.join(self.folder_path, f"mobiles/*.json")
        filenames = glob.glob(mobilefilepath)
        for eachfile in filenames:
            with open(eachfile, 'r') as thefile:
                mobile.Mobile(self, thefile.read())

        # Load each Object in to the Indexes.
        log.info(f"{self.name} : Loading area Objects")
        objectfilepath = os.path.join(self.folder_path, f"objects/*.json")
        filenames = glob.glob(objectfilepath)
        for eachfile in filenames:
            with open(eachfile, 'r') as thefile:
                objects.Object(self, thefile.read(), load_type="index")

        # Load the resets for this area.
        log.info(f"{self.name} : Loading area Resets")
        resetfilepath = os.path.join(self.folder_path, f"resets/resets.json")
        if os.path.exists(resetfilepath):
            with open(resetfilepath, 'r') as thefile:
                areset = reset.Reset(self)
                await areset.load(thefile.read())

        # Add this area to the area list.
        log.info(f"{self.name} : Appending to arealist.")
        arealist.append(self)

    def display(self):
        return(f"{{BName{{x: {self.name}\n"
               f"{{BAuthor{{x: {self.author}\n"
               f"{{BPlane{{x: {self.plane}\n"
               f"{{BHometown{{x: {self.hometown}\n"
               f"{{BDifficulty{{x: {self.difficulty}\n"
               f"{{BAlignment{{x: {self.alignment}\n"
               f"{{BLocation X{{x: {self.locationx}\n"
               f"{{BLocation Y{{x: {self.locationy}\n"
               f"{{BVnum Low{{x: {self.vnumlow}\n"
               f"{{BVnum High{{x: {self.vnumhigh}\n")
