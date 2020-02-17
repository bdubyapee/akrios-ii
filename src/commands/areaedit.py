# Project: Akrios
# Filename: commands/areaedit.py
#
# Capability: builder
#
# Command Description: Entry into area editing mode for builders and admins.
#
# By: Jubelo

from commands import *

name = "areaedit"
version = 1

requirements = {'capability': ['admin'],
                'generic_fail': "See {WHelp areaedit{x for help with this command.",
                'truth_checks':  ['is_standing'],
                'false_checks': []}


@Command(**requirements)
async def areaedit(caller, args, **kwargs):
    helpstring = "Please see {Whelp areaedit{x for instructions."
    args = args.split()

    if not args:
        if caller.is_building:
            await caller.write(caller.building.display())
            return

    if caller.is_building:
        if args[0] == 'done':
            caller.building.save()
            caller.building.builder = None
            del caller.building
            caller.prompt = caller.oldprompt
            del caller.oldprompt
        elif args[0] == 'new':
            await caller.write("You are already editing an area.")
        elif args[0] == 'populate':
            myarea = caller.building
            myvnum = caller.building.vnumlow
            room_exists = area.room_by_vnum_global(myvnum)
            if room_exists:
                await caller.write("That room already exists.  Please edit it directly.")
                return
            else:
                newroom = room.Room(caller.building, vnum=myvnum)
                newroom.area.roomlist[myvnum] = newroom
                await caller.write(f"First new room {newroom.vnum} has been created.")
        elif args[0] in caller.building.commands:
            caller.building.doAttrib(args[0], ' '.join(args[1:]))
        else:
            await caller.write(helpstring)
    else:
        if args[0] == 'new':
            path = os.path.join(world.areaDir, ' '.join(args[1:]))
            if not os.path.exists(path):
                os.makedirs(path)
            else:
                await caller.write("That area exists!")
                return
            header_path = os.path.join(path, f"{' '.join(args[1:])}.json")
            newarea = area.Area(path, header_path)
            caller.building = newarea
            area.arealist.append(newarea)
            caller.building.builder = caller
            await caller.write(f"Editing {{W{args[1:]}{{x")
            caller.oldprompt = caller.prompt
            caller.prompt = "areaEdit:> "
        elif args[0] == 'save':
            caller.location.area.save()
            await caller.write("Area has been saved.")
        elif args[0] == 'here':
            caller.building = caller.location.area
            caller.building.builder = caller
            await caller.write(f"Editing area: {{W{caller.location.area.name}{{x.")
            await caller.write(helpstring)
            caller.oldprompt = caller.prompt
            caller.prompt = "areaEdit:> "
            await caller.write(caller.building.display())
        else:
            await caller.write(helpstring)


