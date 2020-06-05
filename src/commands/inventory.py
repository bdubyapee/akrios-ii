#! /usr/bin/env python3
# Project: Akrios
# Filename: commands/inventoy.py
#
# Capability: player, mobile
#
# Command Description: A command which players can use to check their inventory.
#
#
# By: Jubelo

from commands import *

name = "inventory"
version = 1

requirements = {'capability': ['player', 'mobile'],
                'generic_fail': "See {WHelp inventory{x for help with this command.",
                'truth_checks':  [],
                'false_checks': []}


@Command(**requirements)
async def inventory(caller, args, **kwarg):
    buffer = outbuffer.OutBuffer(caller)

    buffer.add("Items currently in your inventory:")
    buffer.add("")

    if not caller.contents or len(caller.contents) == 0:
        buffer.add("You are carrying nothing.")
        await buffer.write()
        return

    for aid, object_ in caller.contents.items():
        if aid not in caller.equipped.values():
            buffer.add(f"       {object_.disp_name:45}")

    await buffer.write()
