#! usr/bin/env python3
# Project: Akrios
# filename: commands/wield.py
#
# Capability : player, mobile
#
# Command Description: The wield command for players.
#
# By: Jubelo

from commands import *
import comm

name = "wield"
version = 1

requirements = {'capability': ['player', 'mobile'],
                'generic_fail': "See {WHelp wield{x for help with this command.",
                'truth_checks':  [],
                'false_checks': ['is_sleeping']}


@Command(**requirements)
async def wield(caller, args, **kwargs):
    target = None
    args = args.lower()
    
    if not args:
        await caller.write("What would you like to wield?")
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
        await caller.write(f"You don't seem to have a {args}.")
        return

    available_hand_slots = [x for x in caller.equipped if 'hand' in x]

    worn = False

    for each_loc in available_hand_slots:
        if not caller.equipped[each_loc]:
            caller.equipped[each_loc] = target.aid
            await caller.write(f"You wield a {target.disp_name} in your {each_loc}")
            await comm.message_to_room(caller.location, caller, f"{caller.disp_name} wields a {target.disp_name}")
            worn = True
            break

    if not worn:
        await caller.write("Your hands are full!")
