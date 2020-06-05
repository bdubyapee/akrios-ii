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
    buffer = outbuffer.OutBuffer(caller)
    buffer_target = outbuffer.OutBuffer(target)

    buffer_target.add(f"\n\r{{y{caller.disp_name} tells you, '{message}'{{x.")
    await buffer_target.write()

    buffer.add(f"\n\r{{yYou tell {target.disp_name}, '{message}'{{x.")
    await buffer.write()

