# Project: Akrios
# Filename: commands/tell.py
#
# Capability: player
#
# Command Description: Sends a tell to another player.
#
# By: Jubelo

from commands import *

name = "tell"
version = 1


requirements = {'capability': ['player', 'mobile'],
                'generic_fail': "See {WHelp tell{x for help with this command.",
                'truth_checks':  [],
                'false_checks': [],
                'target': 'target_single_player_game_post'}


@Command(**requirements)
async def tell(caller, args, **kwargs):
    target = kwargs['target']
    message = kwargs['post']
    await target.write(f"\n\r{{y{caller.disp_name} tells you, '{message}'{{x.")
    await caller.write(f"\n\r{{yYou tell {target.disp_name}, '{message}'{{x.")
