#! /usr/bin/env python3
# Project: Akrios
# filename: commands/stand.py
#
# Capability: player
#
# Command Description: Allows the player to stand up.
#
#
# By: Jubelo

from commands import *
import comm

name = "stand"
version = 1

requirements = {'capability': ['player', 'mobile'],
                'generic_fail': "See {WHelp stand{x for help with this command.",
                'truth_checks':  [],
                'false_checks': []}


@Command(**requirements)
async def stand(caller, args, **kwargs):
    if caller.position == "standing":
        await caller.write("You are already standing")
        return
    elif caller.position == "sitting":
        caller.position = "standing"
        await caller.write("You stand up.")
        message = f"{caller.disp_name} stands up."
        await comm.message_to_room(caller.location, caller, message)
        return
    elif caller.position == "sleeping":
        caller.position = "standing"
        await caller.write("You awaken and stand up.")
        message = f"{caller.disp_name} stands up."
        await comm.message_to_room(caller.location, caller, message)
        await caller.interp("look")
        return
