#! usr/bin/env python3
# Project: Akrios
# filename: commands/softboot.py
#
# Capability : admin
#
# Command Description: This command soft boots the game.
#
#
#
# By: Jubelo

from commands import *

name = "softboot"
version = 1

requirements = {'capability': ['admin'],
                'generic_fail': "See {WHelp softboot{x for help with this command.",
                'truth_checks':  [],
                'false_checks': []}


@Command(**requirements)
async def softboot(caller, args, **kwargs):
    for each_player in player.playerlist:
        if each_player.is_building or each_player.is_editing:
            await caller.write(f"{each_player.disp_name} is Building right now! No Softboot for you!")
            return

    status.server['running'] = False
    status.server['softboot'] = True
