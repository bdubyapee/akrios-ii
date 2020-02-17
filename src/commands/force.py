# Project: Akrios
# Filename: commands/force.py
#
# Capability: admin
#
# Command Description: Admin level command to "force" something to interp something
#
# By: Jubelo

from commands import *

name = "force"
version = 1

requirements = {'capability': ['admin'],
                'generic_fail': "See {WHelp force{x for help with this command.",
                'truth_checks':  ['args_required'],
                'false_checks': []}


@Command(**requirements)
async def force(caller, args, **kwargs):
    args = args.split()

    target_name = args[0]
    command = ' '.join(args[1:])
    target_obj = None

    for eachthing in caller.location.contents:
        if hasattr(eachthing, "interp") and eachthing.name == target_name.lower():
            target_obj = eachthing

    if target_obj is not None:
        target_obj.interp(command)
        
    await caller.write(f"You forced {target_obj.name} to {command}.")
