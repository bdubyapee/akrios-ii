#! /usr/bin/env python3
# Project: Akrios
# filename: commands/sit.py
#
# Capability: player
#
# Command Description: Allows the player to sit down.
#
#
# By: Jubelo

from commands import *
import comm

name = "sit"
version = 1

requirements = {'capability': ['player', 'mobile'],
                'generic_fail': "See {WHelp sit{x for help with this command.",
                'truth_checks':  [],
                'false_checks': []}


@Command(**requirements)
async def sit(caller, args, **kwargs):
    if hasattr(caller, "position"):
        if caller.position == "sitting":
            await caller.write("You are already sitting")
            return
        elif caller.position == "standing":
            caller.position = "sitting"
            await caller.write("You sit down.")
            message = f"{caller.disp_name} sits down."
            await comm.message_to_room(caller.location, caller, message)
            return
        elif caller.position == "sleeping":
            caller.position = "sitting"
            await caller.write("You wake up and begin sitting")
            message = f"{caller.disp_name} sits up and looks around."
            await comm.message_to_room(caller.location, caller, message)
            await caller.interp("look")
            return
