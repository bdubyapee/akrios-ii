# Project: Akrios
# Filename: commands/playerinfo.py
#
# Capability: admin
#
# Command Description: Allows admins to view additional details about players
#
# By: Jubelo

from commands import *

name = "playerinfo"
version = 1

requirements = {'capability': ['admin'],
                'generic_fail': "See {WHelp playerinfo{x for help with this command.",
                'truth_checks':  [],
                'false_checks': []}


@Command(**requirements)
async def playerinfo(caller, args):
    for person in player.playerlist:
        await caller.write(f"Player: {person.disp_name:15} "
                           f"Host: {person.sock.host:15} ")
