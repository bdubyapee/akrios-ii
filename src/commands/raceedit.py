# Project: Akrios
# Filename: commands/raceedit.py
#
# Capability: admin
#
# Command Description: Utilized to add and modify races
#
# By: Jubelo

from commands import *

name = "raceedit"
version = 1

requirements = {'capability': ['admin'],
                'generic_fail': "See {WHelp raceedit{x for help with this command.",
                'truth_checks':  [],
                'false_checks': []}


@Command(**requirements)
async def raceedit(caller, args, **kwargs):
    helpstring = "Please see {Whelp raceedit{x for instructions."
    args = args.split()
    buffer = outbuffer.OutBuffer(caller)

    if len(args) == 0:
        if caller.is_building and not caller.is_editing:
            buffer.add(caller.building.display())
            await buffer.write()
            return
        elif not caller.is_building:
            buffer.add(helpstring)
            await buffer.write()
            return

    if caller.is_building and caller.is_editing:
        done = False
        if len(args) != 0:
            if args[0].lower() in caller.editing.commands:
                done = caller.editing.commands[args[0].lower()](' '.join(args[1:]))
                if done is True:
                    caller.building.description = caller.editing.lines
                    caller.editing.lines = None
                    del caller.editing
                    del caller.editing_obj_name
                    return
                else:
                    if done is False:
                        return
                    else:
                        buffer.add(done)
                        await buffer.write()
            else:
                caller.editing.add(' '.join(args))
        else:
            caller.editing.add('\n\r')
        return

    if caller.is_building:
        if args[0] == 'done':
            caller.building.save()
            races.racesdict[caller.building.name] = caller.building
            caller.building.builder = None
            del caller.building
            caller.prompt = caller.oldprompt
            del caller.oldprompt
        elif args[0] == 'new':
            buffer.add("You are already editing a race entry.")
            await buffer.write()
            return
        elif args[0] in caller.building.commands:
            caller.building.doAttrib(args[0], ' '.join(args[1:]))
        else:
            buffer.add(helpstring)
            await buffer.write()
    else:
        if args[0] == 'new':
            if len(args) != 2 or args[1] in races.racesdict:
                buffer.add(helpstring)
                await buffer.write()
                return
            else:
                caller.building = races.Race(world.raceDir + f"/{args[1]}")
                caller.building.builder = caller
                buffer.add(f"Editing {{W{args[1]}{{x")
                await buffer.write()
                caller.oldprompt = caller.prompt
                caller.prompt = "raceEdit:> "
        elif args[0] == 'reload':
            races.reload()
            buffer.add("All races have been reloaded.")
            await buffer.write()
        elif args[0] in races.racesdict:
            caller.building = races.racesdict[args[0]]
            caller.building.builder = caller
            buffer.add(f"Editing race: {{W{args[0]}{{x.")
            buffer.add(helpstring)
            caller.oldprompt = caller.prompt
            caller.prompt = "raceEdit:> "
            buffer.add(caller.building.display())
            await buffer.write()
        else:
            buffer.add(helpstring)
            await buffer.write()
