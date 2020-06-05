# Project: Akrios
# Filename: commands/close.py
#
# Capability: player
# 
# Command Description: Allows a player to close a thing.  Exits only for now.
#
#
# By: Jubelo

from commands import *

name = "close"
version = 1

requirements = {'capability': ['player', 'mobile'],
                'generic_fail': "See {WHelp close{x for help with this command.",
                'truth_checks':  [],
                'false_checks': ['is_sleeping']}


@Command(**requirements)
async def close(caller, args, **kwargs):
    buffer = outbuffer.OutBuffer(caller)

    if args in caller.location.exits:
        exit_ = caller.location.exits[args]
        if exit_.destination in caller.location.area.roomlist:
            # Does the exit have a door and is it closed?
            if exit_.hasdoor == 'true':
                if exit_.locked == 'true' or exit_.magiclocked == 'true':
                    buffer.add("It won't open!")
                    await buffer.write()
                    return
                if exit_.dooropen == 'true':
                    exit_.dooropen = 'false'
                    buffer.add(f"You close the {exit_.keywords[0]}.")
                    await buffer.write()
                    return
                if exit_.dooropen == 'false':
                    buffer.add("But it' already closed!")
                    await buffer.write()
                    return
            else:
                buffer.add("There is no door in that direction")
                await buffer.write()
                return
        else:
            # ReWrite this because we'll have exits to other areas and/or the map.
            buffer.add("That exit appears to be broken!")
            await buffer.write()
    else:
        buffer.add("There is no door in that direction")
        await buffer.write()
