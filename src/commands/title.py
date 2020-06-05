# Project: Akrios
# Filename: commands/title.py
#
# Capability: player
#
# Command Description: Allows a player to modify their title for the "who" list.
#
# By: Jubelo

from commands import *

name = "title"
version = 1

requirements = {'capability': ['player'],
                'generic_fail': "See {WHelp title{x for help with this command.",
                'truth_checks':  ['args_required'],
                'false_checks': []}


@Command(**requirements)
async def title(caller, args, **kwargs):
    caller.title = args[:50]
    buffer = outbuffer.OutBuffer(caller)

    buffer.add('{xYour title has been set.')
    await buffer.write()

