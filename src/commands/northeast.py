# Project: Akrios
# Filename: commands/northeast.py
#
# Capability: player
#
# Command Description: Command to move a player northeast
#
# By: Jubelo

from commands import *

name = "northeast"
version = 1


@Command(capability=["player", "mobile", "object"])
async def northeast(caller, args, **kwargs):
    await Command.commandhash['move'](caller, 'northeast')
