#! /usr/bin/env python3
# Project: Akrios
# Filename: commands/save.py
#
# Capability : player
#
# Command Description: This command saves the player data to disk immediatly.
#
# By: Jubelo

from commands import *

name = "save"
version = 1

requirements = {'capability': ['player'],
                'generic_fail': "See {WHelp save{x for help with this command.",
                'truth_checks':  [],
                'false_checks': []}


@Command(**requirements)
async def save(caller, args, **kwargs):
    buffer = outbuffer.OutBuffer(caller)

    caller.save()
    buffer.add("Saved.  Your character is also automatically saved every 5 minutes.")
    await buffer.write()
