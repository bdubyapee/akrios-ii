# Project: Akrios
# Filename: commands/southwest.py
#
# Capability: player
#
# Command Description: Command to move a player southwest
#
# By: Jubelo

from commands import *

name = "southwest"
version = 1


@Command(capability=["player", "mobile", "object"])
async def southwest(caller, args, **kwargs):
    await Command.commandhash['move'](caller, 'southwest')
