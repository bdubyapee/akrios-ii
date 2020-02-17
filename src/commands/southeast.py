# Project: Akrios
# Filename: commands/southeast.py
#
# Capability: player
#
# Command Description: Command to move a player southeast
#
# By: Jubelo

from commands import *

name = "southeast"
version = 1


@Command(capability=["player", "mobile", "object"])
async def southeast(caller, args, **kwargs):
    await Command.commandhash['move'](caller, 'southeast')
