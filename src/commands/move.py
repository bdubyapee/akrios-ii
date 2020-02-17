# Project: Akrios
# Filename: commands/move.py
#
# Capability: player
# 
# Command Description: Underlying command for a player to move in a direction
#
#
# By: Jubelo

from commands import *

name = "move"
version = 1


requirements = {'capability': ['player', 'mobile', 'object'],
                'generic_fail': "See {WHelp move{x for help with this command.",
                'truth_checks':  [],
                'false_checks': ['is_sitting', 'is_sleeping']}


@Command(**requirements)
async def move(caller, args, **kwargs):
    if args in caller.location.exits:
        exit_ = caller.location.exits[args]
        if exit_.destination in caller.location.area.roomlist:
            # Does the exit have a door and is it closed?
            if exit_.hasdoor == 'true' and exit_.dooropen == 'false':
                await caller.write("The door in that direction is closed.")
                return
            # Are we too tall to fit in that exit?
            heightnow = caller.height['feet'] * 12 + caller.height['inches']
            if exits.exit_sizes[exit_.size].height < heightnow:
                await caller.write("You will not fit!")
                return

            # We have passed all validity checks to move.  Housekeeping and move the thing.
            if caller.is_player and caller.is_building:
                await Command.commandhash['roomedit'](caller, 'done')
                was_building = True
            else:
                was_building = False
            newroom = caller.location.area.room_by_vnum(exit_.destination)
            await caller.move(newroom, caller.location, args)
            await caller.interp("look", forced=True)
            if was_building:
                await Command.commandhash['roomedit'](caller, str(exit_.destination))
        else:
            await caller.write("That exit appears to be broken!")
    else:
        await caller.write("You can't go in that direction.")

