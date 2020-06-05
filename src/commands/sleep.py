#! /usr/bin/env python3
# Project: Akrios
# filename: commands/sleep.py
#
# Capability: player
#
# Command Description: Allows the player to sleep.
#
#
# By: Jubelo

from commands import *
import comm

name = "sleep"
version = 1

requirements = {'capability': ['player', 'mobile'],
                'generic_fail': "See {WHelp sleep{x for help with this command.",
                'truth_checks':  [],
                'false_checks': []}


@Command(**requirements)
async def sleep(caller, args, **kwargs):
    buffer = outbuffer.OutBuffer(caller)

    if caller.position == "sleeping":
        buffer.add("You are already sleeping.")
        await buffer.write()
    elif caller.position == "standing" or caller.position == "sitting":
        caller.position = "sleeping"
        buffer.add("You lay down and go to sleep.")
        await buffer.write()
        message = f"{caller.disp_name} lays down to sleep."
        await comm.message_to_room(caller.location, caller, message)
