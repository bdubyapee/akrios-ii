# Project: Akrios
# Filename: commands/whisper.py
#
# Capability: player
#
# Command Description: Allows the player to whisper something to a player in the room they are in.
#
# By Jubelo

from commands import *

name = "whisper"
version = 1


requirements = {'capability': ['player', 'mobile', 'object'],
                'generic_fail': "See {WHelp whisper{x for help with this command.",
                'truth_checks':  [],
                'false_checks': ['is_sleeping'],
                'target': 'target_single_thing_room_post'}


@Command(**requirements)
async def whisper(caller, args, **kwargs):
    target = kwargs['target']
    message = kwargs['post']
    buffer = outbuffer.OutBuffer(caller)
    buffer_target = outbuffer.OutBuffer(target)

    buffer_target.add(f"\n\r{{g{caller.disp_name} whispers to you, '{message}'{{x.")
    await buffer_target.write()
    buffer.add(f"\n\r{{gYou whisper to {target.disp_name}, '{message}'{{x.")
    await buffer.write()
