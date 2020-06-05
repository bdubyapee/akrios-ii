# Project: Akrios
# Filename: commands/areastats.py
#
# Capability: builder
#
# Command Description: Provides details about the area currently in.
#
# By: Jubelo

from commands import *

name = "areastats"
version = 1

requirements = {'capability': ['builder'],
                'generic_fail': "See {WHelp areastats{x for help with this command.",
                'truth_checks':  [],
                'false_checks': []}


@Command(**requirements)
async def areastats(caller, args, **kwargs):
    buffer = outbuffer.OutBuffer(caller)

    buffer.add(caller.location.area.display())
    buffer.add("")
    buffer.add("{RRooms in this area{x:")
    for one_room in caller.location.area.roomlist:
        current_room = caller.location.area.roomlist[one_room]
        buffer.add(f"{{W[{{B{current_room.vnum}{{W]{{x {current_room.name.capitalize()}")

    await buffer.write()
