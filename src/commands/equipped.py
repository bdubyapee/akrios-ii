#! /usr/bin/env python3
# Project: Akrios
# Filename: commands/equipped.py
#
# Capability: player, mobile
#
# Command Description: A command which players can use to check their equipped items.
#
#
# By: Jubelo

from commands import *

name = "equipped"
version = 1

requirements = {'capability': ['player', 'mobile'],
                'generic_fail': "See {WHelp equipped{x for help with this command.",
                'truth_checks':  [],
                'false_checks': []}


@Command(**requirements)
async def equipped(caller, args, **kwarg):
    buffer = outbuffer.OutBuffer(caller)

    buffer.add("Items currently equipped:")
    buffer.add("")

    for each_loc, each_aid in caller.equipped.items():
        if caller.equipped[each_loc] is None:
            eq_name = "nothing"
        else:
            eq_name = caller.contents[each_aid].disp_name

        preface = "worn on "
        if each_loc == "floating nearby":
            preface = ""
        if 'hand' in each_loc:
            preface = "held in "
        if each_loc in ["neck", "waist"]:
            preface = "worn around "
        each_loc = f"{preface}{each_loc}"

        buffer.add(f"      <{each_loc:22}>   {eq_name:40}")

    await buffer.write()
