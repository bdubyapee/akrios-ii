# Project: Akrios
# Filename: commands/prompt.py
#
# Capability: player
#
# Command Description: Allows the player to modify their prompt
#
# By: Jubelo

from commands import *

name = "prompt"
version = 1

requirements = {'capability': ['player'],
                'generic_fail': "See {WHelp prompt{x for help with this command.",
                'truth_checks':  ['args_required'],
                'false_checks': []}


@Command(**requirements)
async def prompt(caller, args, **kwargs):
    caller.prompt = args[:50]
    await caller.write('{xYour prompt has been configured.')

