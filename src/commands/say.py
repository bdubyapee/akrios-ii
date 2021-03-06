# Project: Akrios
# Filename: commands/say.py
#
# Capability: player
#
# Command Description: Allows the player to say something to the room they are in.
#
# By Jubelo

from commands import *

name = "say"
version = 1


requirements = {'capability': ['player', 'mobile', 'object'],
                'generic_fail': "See {WHelp say{x for help with this command.",
                'truth_checks':  [],
                'false_checks': ['is_sleeping'],
                'target': 'target_all_things_room_post'}


@Command(**requirements)
async def say(caller, args, **kwargs):
    target_list = kwargs['target']
    message = kwargs['post']
    buffer = outbuffer.OutBuffer(caller)
       
    buffer.add(f"{{cYou say, '{message[:300]}'")
    await buffer.write()

    for person in target_list:
        if person != caller:
            buffer_target = outbuffer.OutBuffer(person)
            buffer_target.add(f"{{c{caller.disp_name} says, '{message[:300]}'")
            await buffer.write()

