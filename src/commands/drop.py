#! usr/bin/env python3
# Project: Akrios
# filename: commands/drop.py
#
# Capability : player, mobile
#
# Command Description: The drop command for players.
#
# By: Jubelo

from commands import *
import comm

name = "drop"
version = 1

requirements = {'capability': ['player', 'mobile'],
                'generic_fail': "See {WHelp drop{x for help with this command.",
                'truth_checks':  [],
                'false_checks': ['is_sleeping']}


@Command(**requirements)
async def drop(caller, args, **kwargs):
    target = None
    args = args.lower()
    buffer = outbuffer.OutBuffer(caller)

    equipped_items_matched = {}
    inventory_items_matched = {}

    for aid, object_ in caller.contents.items():
        if object_.disp_name.startswith(args):
            if object_.aid in caller.equipped.values():
                equipped_items_matched[object_.aid] = object_
            else:
                inventory_items_matched[object_.aid] = object_
        for eachkw in object_.keywords:
            thekey = eachkw.lower()
            if thekey.startswith(args):
                if object_.aid in caller.equipped.values():
                    equipped_items_matched[object_.aid] = object_
                else:
                    inventory_items_matched[object_.aid] = object_

    if not equipped_items_matched and not inventory_items_matched:
        buffer.add(f"You don't seem to have a {args}.")
        await buffer.write()
        return

    if not inventory_items_matched and equipped_items_matched:
        buffer.add(f"You need to remove '{args}' before dropping it.")
        await buffer.write()
        return

    matched_inv = list(inventory_items_matched.values())
    
    if len(matched_inv) >= 1:
        target = matched_inv[0]
    else:
        buffer.add(f"Something terribly wrong has happened")
        await buffer.write()

    caller.location.area.objectlist.append(target)
    caller.contents.pop(target.aid)

    target.location = caller.location
    target.location.contents.append(target)
    buffer.add(f"You drop a {target.disp_name}")
    await buffer.write()
    await comm.message_to_room(caller.location, caller, f"{caller.disp_name} drops a {target.disp_name}")
