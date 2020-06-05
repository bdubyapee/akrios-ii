# Project: Akrios
# Filename: commands/emote.py
#
# Capability: player
#
# Command Description: Allows a player to emote to the room, for RP.
#
# By: Jubelo

from commands import *

name = "emote"
version = 1


requirements = {'capability': ['player', 'mobile'],
                'generic_fail': "See {WHelp emote{x for help with this command.",
                'truth_checks':  ['args_required'],
                'false_checks': ['is_sleeping'],
                'target': 'target_all_player_room_post'}


@Command(**requirements)
async def emote(caller, args, **kwargs):
    target_list = kwargs['target']
    args_ = kwargs['post']

    for person in target_list:
        if person == caller:
            prefix = ''
        else:
            prefix = '\n\r'

        buffer_target = outbuffer.OutBuffer(person)
        buffer_target.add(f"\n\r{{g{prefix}{caller.disp_name} {args_[:70]}{{x")

        await buffer_target.write()
