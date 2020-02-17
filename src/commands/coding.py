# Project: Akrios
# Filename: commands/coding.py
#
# Capability: admin
#
# Command Description: Allows an admin player to set a coding flag to indicate to others in
#                      the who listing that they are "afk coding"
#
# By: Jubelo

from commands import *

name = "coding"
version = 1

requirements = {'capability': ['admin'],
                'generic_fail': "See {WHelp coding{x for help with this command.",
                'truth_checks':  [],
                'false_checks': []}


@Command(**requirements)
async def coding(caller, args, **kwargs):
    if caller.oocflags['coding'] is False:
        caller.oocflags['coding'] = True
        await caller.write("You have been placed in coding mode.")
    else:
        caller.oocflags['coding'] = False
        await caller.write('You have been removed from coding mode.')

