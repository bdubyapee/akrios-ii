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

    if len(args) == 0:
        if caller.is_building and not caller.is_ediing:
            await caller.write(caller.building.display())
            return
        elif not caller.is_building:
            await caller.write(helpstring)
            return

    if caller.is_building:
        if args[0] == 'done':
            caller.building.room.area.save()
            caller.building.builder = None
            del caller.building
            caller.prompt = caller.oldprompt
            del caller.oldprompt
        elif args[0] == 'new':
            await caller.write("You are already editing an exit.")
            return
        elif args[0] in caller.building.commands:
            caller.building.doAttrib(args[0], ' '.join(args[1:]))
        else:
            await caller.write(helpstring)
    else:
        if args[0] == 'new':
            if len(args) != 3:
                await caller.write(helpstring)
            else:
                if args[1] in exits.directions:
                    direction = args[1]
                else:
                    await caller.write("Thats not a valid direction.")
                    return
                myarea = caller.location.area
                try:
                    myvnum = int(args[2])
                except:
                    await caller.wrte(helpstring)
                    return
                if myvnum < myarea.vnumlow or myvnum > myarea.vnumhigh:
                    await caller.write("That vnum is not in this areas range!")
                    return
                if direction in caller.location.exits:
                    await caller.write("That exit already exists.")
                    return
                else:
                    # defaultexitdata = "false 0 0 false 0 0 0 none huge false true none"
                    # newexitdata = f"{direction} {myvnum} {defaultexitdata}"
                    newexit = exits.Exit(caller.location, direction)
                    caller.building = newexit
                    caller.location.exits[direction] = newexit
                    caller.building.builder = caller
                    await caller.write(f"Editing {{W{args[1]}{{x")
                    await caller.write(caller.building.display())
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
            await caller.write(f"Editing exit: {{W{args[0]}{{x.")
            await caller.write(helpstring)
            caller.oldprompt = caller.prompt
            caller.prompt = "exitEdit:> "
            await caller.write(caller.building.display())
        else:
            await caller.write(helpstring)
