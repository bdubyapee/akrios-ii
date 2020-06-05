#! /usr/bin/env python3
# Project: Akrios
# Filename: commands/gtell.py
#
# Capability: player
#
# Command Description: This is the tell command for the Grapevine network. It goes
# to a player in another game.
#
# By: Jubelo

from commands import *
import grapevine

name = "gtell"
version = 1

requirements = {'capability': ['player'],
                'generic_fail': "See {WHelp gtell{x for help with this command.",
                'truth_checks':  ['args_required'],
                'false_checks': []}


@Command(**requirements)
async def gtell(caller, args, **kwargs):
    buffer = outbuffer.OutBuffer(caller)

    if caller.oocflags_stored['grapevine'] == 'false':
        buffer.add("You have that command self disabled with the 'toggle' command.")
        await buffer.write()
        return

    target = args.split()[0]
    if '@' in target:
        target, game = target.split('@')
    else:
        buffer.add("Command format is 'gtell player@game <message>'.")
        await buffer.write()
        return

    message = ' '.join(args.split()[1:])

    if game.lower() in ['akrios', 'akriosmud']:
        buffer.add("Just use in-game channels to talk to players on Akrios.")
        await buffer.write()
        return

    asyncio.create_task(grapevine.msg_gen_player_tells(caller.disp_name, game, target, message))

    buffer.add(f"{{GYou Grapevine tell {{y{target}@{game}{{x: '{{G{message}{{x'")
    await buffer.write()
