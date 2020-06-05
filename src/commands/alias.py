#! /usr/bin/env python3
# Project: Akrios
# Filename: commands/alias.py
#
# Capability: player
#
# Command Description: A command which players can use to create an alias for another command.
#                      For example, they can alias 'n' to 'north' to use 'n' to execute 'north'.
#
#
# By: Jubelo

from commands import *

name = "alias"
version = 1

requirements = {'capability': ['player'],
                'generic_fail': "See {WHelp alias{x for help with this command.",
                'truth_checks':  [],
                'false_checks': []}


@Command(**requirements)
async def alias(caller, args, **kwarg):
    args = args.split()
    buffer = outbuffer.OutBuffer(caller)

    if len(args) == 0:
        buffer.add("Current alias' saved:")
        for one in caller.alias.keys():
            buffer.add(f"{one} => {caller.alias[one]}")
        await buffer.write()
        return
    elif args[0] == 'remove' and len(args) == 2:
        if args[1] in caller.alias.keys():
            del caller.alias[args[1]]
            buffer.add("Alias removed.")
            await buffer.write()
        else:
            buffer.add(f"No alias '{args[1]}' to remove.")
            await buffer.write()
        return
    elif args[0] == 'alias':
        buffer.add("See {Whelp alias{x for help with this command.")
        await buffer.write()
        return
    else:
        caller.alias[args[0]] = ' '.join(args[1:])
        buffer.add(f"Alias {args[0]} successfully created.")
        await buffer.write()
