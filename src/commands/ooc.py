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
    buffer = outbuffer.OutBuffer(caller)

    if caller.oocflags_stored['ooc'] == 'false':
        buffer.add("You have the OOC channel disabled.  Use the {Wtoggle{x command to enable it.")
        await buffer.write()
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
            name_ = '' + name_

        buffer_target = outbuffer.OutBuffer(person)
        buffer_target.add(f"{{B{name_} OOC{plural}: '{args_[:300]}'")
        await buffer_target.write()
