#! usr/bin/env python3
# Project: Akrios
# filename: commands/shutdown.py
#
# Capability : admin
#
# Command Description: This command shuts down the game fully.
#
#
#
# By: Jubelo

from commands import *

name = "shutdown"
version = 1

requirements = {'capability': ['admin'],
                'generic_fail': "See {WHelp shutdown{x for help with this command.",
                'truth_checks':  [],
                'false_checks': []}


@Command(**requirements)
async def shutdown(caller, args, **kwargs):
    for each_player in player.playerlist:
        if each_player.is_building or each_player.is_editing:
            await caller.write(f"{each_player.disp_name} is Building right now! No Shutdown for you!")
            return

    status.server['running'] = False
