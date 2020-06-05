#! usr/bin/env python3
# Project: Akrios
# filename: commands/remove.py
#
# Capability : player, mobile
#
# Command Description: The remove command for players.
#
# By: Jubelo

from commands import *
import comm

name = "remove"
version = 1

requirements = {'capability': ['player', 'mobile'],
                'generic_fail': "See {WHelp remove{x for help with this command.",
                'truth_checks':  [],
                'false_checks': ['is_sleeping']}


@Command(**requirements)
async def remove(caller, args, **kwargs):
    """
        Expecting:
                    "helmet"
                    "bracelet from left wrist"
                    "diamond sword"
    """

    target = None
    args = args.lower()
    buffer = outbuffer.OutBuffer(caller)
   
    if not args:
        buffer.add("What would you like to remove?")
        await buffer.write()
        return
 
    if ' from ' in args:
        target_text, location = args.split(' from ')
        target_text = target_text.strip()
        location = location.strip()
    else:
        target_text = args.strip()
        location = None

    for aid, object_ in caller.contents.items():
        if object_.disp_name.startswith(target_text) and object_.aid in caller.equipped.values():
            target = object_
            break
        for eachkw in object_.keywords:
            thekey = eachkw.lower()
            if thekey.startswith(target_text) and object_.aid in caller.equipped.values():
                target = object_
                break

    if target and not location:
        for each_loc, each_item in caller.equipped.items():
            if target.aid == each_item:
                location = each_loc

    if target is None:
        buffer.add(f"You don't seem to be wearing a {args}.")
        await buffer.write()
        return

    if location is not None and location not in caller.equipped:
        buffer.add(f"You cannot remove something from a wear location you don't have.")
        await buffer.write()
        return

    if location is not None and caller.equipped[location] is None:
        buffer.add(f"You are not wearing anything on your {location}")
        await buffer.write()
        return

    if location:
        caller.equipped[location] = None
        buffer.add(f"You remove a {target.disp_name} from your {location}")
        await buffer.write()
        await comm.message_to_room(caller.location, caller, f"{caller.disp_name} removes a {target.disp_name}")
    else:
        buffer.add("Error remove {target.disp_name} from {location}.")
        await buffer.write()
