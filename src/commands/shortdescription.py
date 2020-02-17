# Project: Akrios
# Filename: commands/longdescription.py
#
# Capability: player
#
# Command Description: Allows a player to set their short description
#
# By: Jubelo

from commands import *

name = "shortdescription"
version = 1

requirements = {'capability': ['player'],
                'generic_fail': "See {WHelp shortdescription{x for help with this command.",
                'truth_checks':  ['args_required'],
                'false_checks': []}


@Command(**requirements)
async def shortdescription(caller, args, **kwargs):
    caller.short_description = args[:78]
    
    await caller.write('{xYour short description has been set.')
