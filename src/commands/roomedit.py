# Project: Akrios
# Filename: commands/roomedit.py
#
# Capability: builder
#
# Command Description: Allows builder to edit the room they are in.
#
# By: Jubelo

from commands import *

name = "roomedit"
version = 1

requirements = {'capability': ['builder'],
                'generic_fail': "See {WHelp roomedit{x for help with this command.",
                'truth_checks':  [],
                'false_checks': []}


@Command(**requirements)
async def roomedit(caller, args, **kwargs):
    helpstring = "Please see {Whelp roomedit{x for instructions."
    args = args.split()

    if len(args) == 0:
        if caller.is_building and not caller.is_editing:
            await caller.write(caller.building.display())
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
            caller.building.area.save()
            caller.building.builder = None
            del caller.building
            caller.prompt = caller.oldprompt
            del caller.oldprompt
        elif args[0] == 'new':
            await caller.write("You are already editing a room.")
            return
        elif args[0] in caller.building.commands:
            caller.building.doAttrib(args[0], ' '.join(args[1:]))
        else:
            await caller.write(helpstring)
    else:
        myvnum = 0
        try:
            myvnum = int(args[0])
        except:
            pass
        if len(args) == 0:
            if "room" in caller.location.capability:
                caller.building = caller.location
                caller.building.builder = caller
                await caller.write(f"Editing {{W{caller.location.vnum}{{x")
                caller.oldprompt = caller.prompt
                caller.prompt = "roomEdit:> "
                await caller.write(caller.building.display())
            else:
                await caller.write("Your location does not appear to be a regular room.")
                return
        elif args[0] == 'new':
            if len(args) != 2:
                await caller.write(helpstring)
            else:
                myarea = caller.location.area
                try:
                    myvnum = int(args[1])
                except Exception as err:
                    await caller.write(f"Vnum argument must be an integer, not: {err}")
                    return
                if myvnum < myarea.vnumrange[0] or myvnum > myarea.vnumrange[1]:
                    await caller.write("That vnum is not in this areas range!")
                    return
                if myvnum in myarea.roomlist:
                    await caller.write("That room already exists.  Please edit it directly.")
                    return
                else:
                    newroom = room.Room(caller.location.area, vnum=myvnum)
                    caller.building = newroom
                    newroom.area.roomlist[myvnum] = newroom
                    caller.building.builder = caller
                    await caller.write(f"Editing {{W{args[1]}{{x")
                    caller.oldprompt = caller.prompt
                    caller.prompt = "roomEdit:> "
                    caller.location = caller.building
        elif args[0] == 'save':
            caller.location.area.save()
            await caller.write("Area has been saved.")
        elif args[0] == 'delete':
            try:
                myvnum = int(args[1])
            except Exception as err:
                await caller.write(f"Vnum argument must be an integer, not: {err}")
                return
            if myvnum in caller.location.area.roomlist:
                newroom = area.room_by_vnum_global(1)
                for thing in caller.location.area.roomlist[myvnum].contents:
                    thing.move(newroom, None, "goto")
                caller.location.area.roomlist.pop(myvnum)
                await caller.write(f"Room {myvnum} deleted.")
        elif myvnum in caller.location.area.roomlist:
            caller.building = caller.location.area.roomlist[int(args[0])]
            caller.building.builder = caller
            await caller.write(f"Editing room: {{W{args[0]}{{x.")
            await caller.write(helpstring)
            caller.oldprompt = caller.prompt
            caller.prompt = "roomEdit:> "
            caller.location = caller.building
            await caller.write(caller.building.display())
        else:
            await caller.write(helpstring)
