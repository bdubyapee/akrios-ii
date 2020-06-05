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
    buffer = outbuffer.OutBuffer(caller)

    if caller.position == "standing":
        buffer.add("You are already standing")
        await buffer.write()
        return
    elif caller.position == "sitting":
        caller.position = "standing"
        buffer.add("You stand up.")
        await buffer.write()
        message = f"{caller.disp_name} stands up."
        await comm.message_to_room(caller.location, caller, message)
        return
    elif caller.position == "sleeping":
        caller.position = "standing"
        buffer.add("You awaken and stand up.")
        await buffer.write()
        message = f"{caller.disp_name} stands up."
        await comm.message_to_room(caller.location, caller, message)
        await caller.interp("look")
        return
