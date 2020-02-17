#! /usr/bin/env python3
# Project: Akrios
# filename: commands/afk.py
#
# Capability: player
#
# Command Description: Away From Keyboard (AFK) toggler for player away
#                      indication to other players and self.
#
#
# By: Jubelo

from commands import *

name = "afk"
version = 1

requirements = {'capability': ['player'],
                'generic_fail': "See {WHelp afk{x for help with this command.",
                'truth_checks':  [],
                'false_checks': []}


@Command(**requirements)
async def afk(caller, args, **kwargs):
    if caller.oocflags['afk']:
        caller.oocflags['afk'] = False
        await caller.write("AFK mode removed.")
    else:
        caller.oocflags['afk'] = True
        await caller.write('You have been placed in AFK mode.')

