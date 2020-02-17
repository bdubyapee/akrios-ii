# Project: Akrios
# Filename: commands/northwest.py
#
# Capability: player
#
# Command Description: Command to move a player northwest
#
# By: Jubelo

from commands import *

name = "northwest"
version = 1


@Command(capability=["player", "mobile", "object"])
async def northwest(caller, args, **kwargs):
    await Command.commandhash['move'](caller, 'northwest')
