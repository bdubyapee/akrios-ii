#! usr/bin/env python3
# Project: Akrios
# filename: commands/wear.py
#
# Capability : player, mobile
#
# Command Description: The wear command for players.
#
# By: Jubelo

from commands import *
import comm

name = "wear"
version = 1

requirements = {'capability': ['player', 'mobile'],
                'generic_fail': "See {WHelp wear{x for help with this command.",
                'truth_checks':  [],
                'false_checks': ['is_sleeping']}


@Command(**requirements)
async def wear(caller, args, **kwargs):
    """
        Expecting:
                    "helmet on head"
                    "bracelet on left wrist"
    """

    target = None
    location = None
    args = args.lower()
    buffer = outbuffer.OutBuffer(caller)

    if not args:
        buffer.add("What would you like to wear?")
        await buffer.write()
        return

    if ' on ' in args:
        target_text, location = args.split(' on ')
        target_text = target_text.strip()
        location = location.strip()
    else:
        buffer.add("Please specify where to wear it.")
        buffer.add("Example: wear helmet on head.")
        await buffer.write()
        return

    for aid, object_ in caller.contents.items():
        if object_.disp_name.startswith(target_text) and aid not in caller.equipped.values():
            target = object_
            break
        for eachkw in object_.keywords:
            thekey = eachkw.lower()
            if thekey.startswith(target_text) and aid not in caller.equipped.values():
                target = object_
                break

    if target is None:
        buffer.add(f"You don't seem to have a {args}.")
        await buffer.write()
        return

    if location not in caller.equipped:
        buffer.add(f"You cannot wear something on a wear location you don't have.")
        await buffer.write()
        return

    if location is not None and caller.equipped[location] is not None:
        buffer.add(f"You are already wearing something in that location.")
        await buffer.write()
        return

    if location not in target.allowable_wear_loc:
        buffer.add(f"You cannot wear a {args} there!")
        await buffer.write()
        return

    caller.equipped[location] = target.aid

    if 'hand' in location:
        buffer.add(f"You hold a {target.disp_name} in your {location}")
        await comm.message_to_room(caller.location, caller, f"{caller.disp_name} holds a {target.disp_name}.")
    else:
        buffer.add(f"You wear a {target.disp_name} on your {location}.")
        await comm.message_to_room(caller.location, caller, f"{caller.disp_name} wears a {target.disp_name}.")

    await buffer.write()
