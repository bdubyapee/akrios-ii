# Project: Akrios
# Filename: commands/arealist.py
#
# Capability: player
#
# Command Description: Provides the player with a list of areas
#
# By: Jubelo

from commands import *

name = "arealist"
version = 1

requirements = {'capability': ['player'],
                'generic_fail': "See {WHelp arealist{x for help with this command.",
                'truth_checks':  [],
                'false_checks': []}


@Command(**requirements)
async def arealist(caller, args, **kwargs):
    
    see_vnums = False

    if caller.is_deity or caller.is_builder or caller.is_admin:
        see_vnums = True

    for eacharea in area.arealist:
        vnum_string = ""
        if see_vnums:
            vnum_string = f"{{W[{{B{eacharea.vnumlow:<6} - {eacharea.vnumhigh:>6}{{W]{{x  "
        name_ = eacharea.name.capitalize()
        diff = eacharea.difficulty.capitalize()

        await caller.write(f"{vnum_string}{{W[ {{B{diff:<8}{{W ]{{x {name_}")
    await caller.write("")
