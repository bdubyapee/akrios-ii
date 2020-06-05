#! usr/bin/env python3
# Project: Akrios
# filename: commands/get.py
#
# Capability : player, mobile
#
# Command Description: The get command for players.
#
# By: Jubelo

from commands import *
import comm

name = "get"
version = 1

requirements = {'capability': ['player', 'mobile'],
                'generic_fail': "See {WHelp get{x for help with this command.",
                'truth_checks':  [],
                'false_checks': ['is_sleeping'],
                'target': 'target_single_thing_room_nopost'}


@Command(**requirements)
async def get(caller, args, **kwargs):
    target = kwargs['target']
    buffer = outbuffer.OutBuffer(caller)
    
    # Check weight of thing picked up or cancel

    if target.is_mobile or target.is_player:
        buffer.add("You cannot pick up players or mobiles. Yet.")
        await buffer.write()
        return

    caller.contents[target.aid] = target
    target.location.contents.remove(target)
    target.location = None
    if target in caller.location.area.objectlist:
        caller.location.area.objectlist.remove(target)

    buffer.add(f"You pick up a {target.disp_name}")
    await buffer.write()
    await comm.message_to_room(caller.location, caller, f"{caller.disp_name} picks up a {target.disp_name}")
