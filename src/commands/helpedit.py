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

    if len(args) == 0:
        if caller.is_building and not caller.is_editing:
            await caller.write(caller.building.display())
            return
        elif not caller.is_building:
            await caller.write(helpstring)
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
            await caller.write("You are already editing a help entry.")
            return
        elif args[0] in caller.building.commands:
            try:
                caller.building.doAttrib(args[0], ' '.join(args[1:]))
            except:
                await caller.write("There was an error processing that request.  Possible options are:")
                theoptions = ", ".join(caller.building.commands[args[0]][1].keys())
                await caller.write(f"    {{W{theoptions}{{x")
                return
        else:
            await caller.write(helpstring)
    else:
        if args[0] == 'new':
            if len(args) != 2 or args[1] in helpsys.helpfiles:
                await caller.write(helpstring)
                return
            else:
                caller.building = helpsys.Help(f"{world.helpDir}/{args[1]}.json")
                caller.building.builder = caller
                await caller.write(caller.building.display())
                await caller.write(f"Editing {{W{args[0]}{{x help entry.")
                await caller.write("Please visit {Whelp helpedit{x for details.\n\r")
                caller.oldprompt = caller.prompt
                caller.prompt = "hEdit:> "
        elif args[0] == 'reload':
            helpsys.reload()
            await caller.write("All helpfiles have been reloaded.")
        elif args[0] in helpsys.helpfiles:
            caller.building = helpsys.helpfiles[args[0]]
            caller.building.builder = caller
            await caller.write(f"Editing {{W{args[0]}{{x help entry.")
            await caller.write("Please visit {Whelp helpedit{x for details.\n\r")
            caller.oldprompt = caller.prompt
            caller.prompt = "hEdit:> "
            await caller.write(caller.building.display())
        else:
            await caller.write(helpstring)

