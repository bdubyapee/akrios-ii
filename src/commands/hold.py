#! usr/bin/env python3
# Project: Akrios
# filename: commands/hold.py
#
# Capability : player, mobile
#
# Command Description: The hold command for players.
#
# By: Jubelo

from commands import *
import comm

name = "hold"
version = 1

requirements = {'capability': ['player', 'mobile'],
                'generic_fail': "See {WHelp hold{x for help with this command.",
                'truth_checks':  [],
                'false_checks': ['is_sleeping']}


@Command(**requirements)
async def hold(caller, args, **kwargs):
    target = None
    args = args.lower()
    buffer = outbuffer.OutBuffer(caller)
    
    if not args:
        buffer.add("What would you like to hold?")
        await buffer.write()
        return

    for aid, object_ in caller.contents.items():
        if object_.disp_name.startswith(args) and aid not in caller.equipped.values():
            target = object_
            break
        for eachkw in object_.keywords:
            thekey = eachkw.lower()
            if thekey.startswith(args) and aid not in caller.equipped.values():
                target = object_
                break

    if target is None:
        buffer.add(f"You don't seem to have a {args}.")
        await buffer.write()
        return

    available_hand_slots = [x for x in caller.equipped if 'hand' in x]

    worn = False

    for each_loc in available_hand_slots:
        if not caller.equipped[each_loc]:
            caller.equipped[each_loc] = target.aid
            buffer.add(f"You hold a {target.disp_name} in your {each_loc}")
            await buffer.write()
            await comm.message_to_room(caller.location, caller, f"{caller.disp_name} holds a {target.disp_name}")
            worn = True
            break

    if not worn:
        buffer.add("Your hands are full!")
        await buffer.write()
