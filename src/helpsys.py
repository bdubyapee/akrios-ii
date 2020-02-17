#! usr/bin/env python
# Project: Akrios
# Filename: helpsys.py
# 
# File Description: Module to handle the help system.
# 
# By: Jubelo

from collections import namedtuple
import glob
import logging
import json
import os

import olc
import world

log = logging.getLogger(__name__)

WRITE_NEW_FILE_VERSION = False

# Define some named tuples for various Help file values
Section = namedtuple("Section", "name")

sections = {"player": Section("player"),
            "administrative": Section("administrative"),
            "builder": Section("builder"),
            "deity": Section("deity")}


class Help(olc.Editable):
    CLASS_NAME = "__Help__"
    FILE_VERSION = 1

    def __init__(self, path):
        super().__init__()
        self.path = path
        self.json_version = Help.FILE_VERSION
        self.json_class_name = Help.CLASS_NAME
        self.builder = None
        self.creator = ""
        self.viewable = ""
        self.keywords = []
        self.topics = ""
        self.section = ""
        self.description = ""
        self.commands = {"viewable": ("string", ["true", "false"]),
                         "creator": ("string", None),
                         "keywords": ("list", None),
                         "topics": ("string", None),
                         "section": ("string", sections),
                         "description": ("description", None)}

        if os.path.exists(path):
            self.load()

    def to_json(self):
        if self.json_version == 1:
            jsonable = {"json_version": self.json_version,
                        "json_class_name": self.json_class_name,
                        "creator": self.creator,
                        "viewable": self.viewable,
                        "keywords": self.keywords,
                        "topics": self.topics,
                        "section": self.section,
                        "description": self.description}
            return json.dumps(jsonable, sort_keys=True, indent=4)

    def load(self):
        log.debug(f"Loading help file: {self.path}")
        if self.path.endswith("json"):
            with open(self.path, "r") as thefile:
                help_file_dict = json.loads(thefile.read())
                for eachkey, eachvalue in help_file_dict.items():
                    setattr(self, eachkey, eachvalue)

    def save(self):
        with open(f"{self.path}", "w") as thefile:
            thefile.write(self.to_json())

    def display(self):
        return (f"{{BCreator{{x: {self.creator}\n"
                f"{{BViewable{{x: {self.viewable}\n"
                f"{{BKeywords{{x: {', '.join(self.keywords)}\n"
                f"{{BTopics{{x: {self.topics}\n"
                f"{{BSection{{x: {self.section}\n"
                f"   {{y{', '.join(sections)}\n"
                f"{{BDescription{{x:\n\r"
                f"{self.description[:190]}|...{{x\n\r")


helpfiles = {}


def init():
    log.info("Initializing all help files.")
    allhelps = glob.glob(os.path.join(world.helpDir, "*.json"))
    for singlehelp in allhelps:
        thehelp = Help(singlehelp)
        for keyword in thehelp.keywords:
            helpfiles[keyword] = thehelp
        if WRITE_NEW_FILE_VERSION:
            thehelp.save()


def reload():
    helpfiles.clear()
    init()


def get_help(key, server=False):
    key = key.lower()
    if key:
        if key in helpfiles:
            if helpfiles[key].viewable.lower() == "true" or server:
                return helpfiles[key].description
        else:
            log.warning(f"MISSING HELP FILE: {key}")
            return "We do not appear to have a help file for that topic. "\
                   "We have however logged the attempt and will look into creating "\
                   "a help file for that topic as soon as possible.\n\r"
