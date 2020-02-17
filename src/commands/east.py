# Project: Akrios
# Filename: commands/east.py
#
# Capability: player
#
# Command Description: Command to move a player east
#
# By: Jubelo

from commands import *

name = "east"
version = 1


@Command(capability=["player", "mobile", "object"])
async def east(caller, args, **kwargs):
    await Command.commandhash['move'](caller, 'east')
