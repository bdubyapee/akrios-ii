# Project: Akrios
# Filename: commands/exitedit.py
#
# Capability: builder
#
# Command Description: Allows Builders to modify and build Exits.
#
# By: Jubelo

from commands import *

name = "exitedit"
version = 1

requirements = {'capability': ['builder'],
                'generic_fail': "See {WHelp exitedit{x for help with this command.",
                'truth_checks':  ['is_standing'],
                'false_checks': []}


@Command(**requirements)
async def exitedit(caller, args, **kwargs):
    helpstring = "Please see {Whelp exitedit{x for instructions."
    args = args.split()
    buffer = outbuffer.OutBuffer(caller)

    if len(args) == 0:
        if caller.is_building and not caller.is_ediing:
            buffer.add(caller.building.display())
            await buffer.write()
            return
        elif not caller.is_building:
            buffer.add(helpstring)
            await buffer.write()
            return

    if caller.is_building:
        if args[0] == 'done':
            caller.building.room.area.save()
            caller.building.builder = None
            del caller.building
            caller.prompt = caller.oldprompt
            del caller.oldprompt
        elif args[0] == 'new':
            buffer.add("You are already editing an exit.")
            await buffer.write()
            return
        elif args[0] in caller.building.commands:
            caller.building.doAttrib(args[0], ' '.join(args[1:]))
        else:
            buffer.add(helpstring)
            await buffer.write()
    else:
        if args[0] == 'new':
            if len(args) != 3:
                buffer.add(helpstring)
                await buffer.write()
            else:
                if args[1] in exits.directions:
                    direction = args[1]
                else:
                    buffer.add("Thats not a valid direction.")
                    await buffer.write()
                    return
                myarea = caller.location.area
                try:
                    myvnum = int(args[2])
                except:
                    buffer.add(helpstring)
                    await buffer.write()
                    return
                if myvnum < myarea.vnumlow or myvnum > myarea.vnumhigh:
                    buffer.add("That vnum is not in this areas range!")
                    await buffer.write()
                    return
                if direction in caller.location.exits:
                    buffer.add("That exit already exists.")
                    await buffer.write()
                    return
                else:
                    # defaultexitdata = "false 0 0 false 0 0 0 none huge false true none"
                    # newexitdata = f"{direction} {myvnum} {defaultexitdata}"
                    newexit = exits.Exit(caller.location, direction)
                    caller.building = newexit
                    caller.location.exits[direction] = newexit
                    caller.building.builder = caller
                    buffer.add(f"Editing {{W{args[1]}{{x")
                    buffer.add(caller.building.display())
                    await buffer.write()
                    caller.oldprompt = caller.prompt
                    caller.prompt = "exitEdit:> "
        elif args[0] == 'delete':
            if args[1] in caller.location.exits:
                caller.location.exits.pop(args[1])
            await caller.write(f"{args[1]} exit has been removed")
        elif args[0] in caller.location.exits:
            direction = args[0]
            caller.building = caller.location.exits[direction]
            caller.building.builder = caller
            buffer.add(f"Editing exit: {{W{args[0]}{{x.")
            buffer.add(helpstring)
            caller.oldprompt = caller.prompt
            caller.prompt = "exitEdit:> "
            buffer.add(caller.building.display())
            await buffer.write()
        else:
            buffer.add(helpstring)
            await buffer.write()
