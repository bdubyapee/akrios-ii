# Project: Akrios
# Filename: commands/promote.py
#
# Capability: admin
#
# Command Description: Allows an Admin to promote another user to a specific capabilities profile.
#
# By: Jubelo

from commands import *

name = "promote"
version = 1

requirements = {'capability': ['admin'],
                'generic_fail': "See {WHelp promote{x for help with this command.",
                'truth_checks':  ['args_required'],
                'false_checks': [],
                'target': 'target_single_player_game_post'}


@Command(**requirements)
async def promote(caller, args, **kwargs):
    target = kwargs['target']
    args_ = kwargs['post']
    status = ''
    buffer = outbuffer.OutBuffer(caller)
    buffer_target = outbuffer.OutBuffer(target)

    if args_ not in ['admin', 'builder', 'deity']:
        buffer.add("That is not a valid promotion option.")
        await buffer.write()
        return
            
    if 'admin' in args_ and 'admin' not in target.capability:
        target.capability.append('admin')
        buffer_target.add("You've been promoted to Admin status!")
        status = 'admin'
    if 'builder' in args_ and 'builder' not in target.capability:
        target.capability.append('builder')
        buffer_target.add("You've been promoted to Builder status!")
        status = 'builder'
    if 'deity' in args_ and 'deity' not in target.capability:
        target.capability.append('deity')
        buffer_target.add("You've been promoted to Deity status!")
        status = 'deity'

    await buffer_target.write()

    target.save()

    buffer.add(f"You have promoted {target.name} to {status} status!")
    await buffer.write()


