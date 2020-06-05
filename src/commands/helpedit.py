# Project: Akrios
# Filename: commands/helpedit.py
#
# Capability: admin
#
# Command Description: Allows administrators to add/remove/update help files.
#
# By: Jubelo

from commands import *

name = "helpedit"
version = 1

requirements = {'capability': ['admin'],
                'generic_fail': "See {WHelp helpedit{x for help with this command.",
                'truth_checks':  [],
                'false_checks': []}


@Command(**requirements)
async def helpedit(caller, args, **kwargs):
    helpstring = "Please see {Whelp helpedit{x for instructions."
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
                        await caller.write(done)
            else:
                caller.editing.add(' '.join(args))
        else:
            caller.editing.add('\n\r')
        return

    if caller.is_building:
        if args[0] == 'done':
            caller.building.save()
            caller.building.load()
            helpsys.helpfiles[caller.building.keywords[0]] = caller.building
            caller.building.builder = None
            del caller.building
            caller.prompt = caller.oldprompt
            del caller.oldprompt
        elif args[0] == 'new':
            buffer.add("You are already editing a help entry.")
            await buffer.write()
            return
        elif args[0] in caller.building.commands:
            try:
                caller.building.doAttrib(args[0], ' '.join(args[1:]))
            except:
                buffer.add("There was an error processing that request.  Possible options are:")
                theoptions = ", ".join(caller.building.commands[args[0]][1].keys())
                buffer.add(f"    {{W{theoptions}{{x")
                await buffer.write()
                return
        else:
            buffer.add(helpstring)
            await buffer.write()
    else:
        if args[0] == 'new':
            if len(args) != 2 or args[1] in helpsys.helpfiles:
                await caller.write(helpstring)
                return
            else:
                caller.building = helpsys.Help(f"{world.helpDir}/{args[1]}.json")
                caller.building.builder = caller
                buffer.add(caller.building.display())
                buffer.add(f"Editing {{W{args[0]}{{x help entry.")
                buffer.add("Please visit {Whelp helpedit{x for details.\n\r")
                await buffer.write()
                caller.oldprompt = caller.prompt
                caller.prompt = "hEdit:> "
        elif args[0] == 'reload':
            helpsys.reload()
            buffer.add("All helpfiles have been reloaded.")
            await buffer.write()
        elif args[0] in helpsys.helpfiles:
            caller.building = helpsys.helpfiles[args[0]]
            caller.building.builder = caller
            buffer.add(f"Editing {{W{args[0]}{{x help entry.")
            buffer.add("Please visit {Whelp helpedit{x for details.\n\r")
            caller.oldprompt = caller.prompt
            caller.prompt = "hEdit:> "
            buffer.add(caller.building.display())
            await buffer.write()
        else:
            buffer.add(helpstring)
            await buffer.write()
