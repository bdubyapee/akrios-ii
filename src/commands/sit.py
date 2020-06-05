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
    buffer = outbuffer.OutBuffer(caller)

    if hasattr(caller, "position"):
        if caller.position == "sitting":
            buffer.add("You are already sitting")
            await buffer.write()
        elif caller.position == "standing":
            caller.position = "sitting"
            buffer.add("You sit down.")
            await buffer.write()
            message = f"{caller.disp_name} sits down."
            await comm.message_to_room(caller.location, caller, message)
        elif caller.position == "sleeping":
            caller.position = "sitting"
            buffer.add("You wake up and begin sitting")
            await buffer.write()
            message = f"{caller.disp_name} sits up and looks around."
            await comm.message_to_room(caller.location, caller, message)
            await caller.interp("look")
