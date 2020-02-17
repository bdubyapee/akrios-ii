#! usr/bin/env python
# Project: Akrios
# Filename: comm.py
# 
# File Description: Communications Module.  Handles low level channel/log stuff.
# 
# By: Jubelo

import logging

log = logging.getLogger(__name__)


def message_to_room(room, sender, message=""):
    if not message:
        return

    for each_thing in room.contents:
        if each_thing is not sender and each_thing.is_player:
            each_thing.write(f"\n\r\n\r{message}")


def message_to_area(area, sender, message=""):
    if not message:
        return

    for each_player in area.playerlist:
        each_player.write(message)
