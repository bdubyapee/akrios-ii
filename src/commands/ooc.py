#! /usr/bin/env python3
# Project: Akrios
# Filename: commands/ooc.py
#
# Capability: player
#
# Command Description: This is the Out of Character (OOC) chat command. It is global, and not RP.
#
# By: Jubelo

from commands import *

name = "ooc"
version = 1

requirements = {'capability': ['player'],
                'generic_fail': "See {WHelp ooc{x for help with this command.",
                'truth_checks':  ['arg_required'],
                'false_checks': [],
                'target': 'target_all_player_game_post'}


@Command(**requirements)
async def ooc(caller, args, **kwargs):
    if caller.oocflags_stored['ooc'] == 'false':
        await caller.write("You have the OOC channel disabled.  Use the {Wtoggle{x command to enable it.")
        return

    target_list = kwargs['target']
    args_ = kwargs['post']
    for person in target_list:
        if person.oocflags_stored['ooc'] == 'false':
            continue
        if person == caller:
            name_ = "You"
            plural = ''
        else:
            name_ = caller.disp_name
            plural = 's'
            name_ = '\n\r' + name_
        await person.write(f"{{B{name_} OOC{plural}: '{args_[:300]}'")
