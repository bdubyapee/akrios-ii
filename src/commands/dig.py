# Project: Akrios
# Filename: commands/dig.py
#
# Capability: builder
#
# Command Description: Allows builder to "dig" to a new room which creates the exist and template.
#
# By: Jubelo

from commands import *

name = "dig"
version = 1

requirements = {'capability': ['builder'],
                'generic_fail': "See {WHelp dig{x for help with this command.",
                'truth_checks':  ['is_standing', 'args_required'],
                'false_checks': []}


@Command(**requirements)
async def dig(caller, args, **kwargs):
    helpstring = "Please see {Whelp dig{x for instructions."
    args = args.split()
    buffer = outbuffer.OutBuffer(caller)

    if args[0] in exits.directions:
        if len(args) != 2:
            buffer.add(helpstring)
            await buffer.write()
            return
        else:
            targetvnum = int(args[1])
            if targetvnum in caller.location.area.roomlist:
                buffer.add(f"Room {{W{targetvnum}{{x already exists!")
                await buffer.write()
                return
            if args[0] in caller.location.exits:
                buffer.add("There is already an exit in that direction!")
                await buffer.write()
                return

            newexitdata = {"direction": args[0],
                           "destination": targetvnum}
            revexitdata = {"direction": exits.oppositedirection[args[0]],
                           "destination": caller.location.vnum}

            new_exit_data_json = json.dumps(newexitdata, sort_keys=True, indent=4)
            rev_exit_data_json = json.dumps(revexitdata, sort_keys=True, indent=4)

            myarea = caller.location.area
            if targetvnum < myarea.vnumlow or targetvnum > myarea.vnumhigh:
                buffer.add("That vnum is not in this areas range!")
                await buffer.write()
                return
            else:
                newroom = room.Room(caller.location.area, vnum=targetvnum)
                newroom.area.roomlist[targetvnum] = newroom
                exits.Exit(targetvnum, None, rev_exit_data_json)
                exits.Exit(caller.location.vnum, None, new_exit_data_json)
                buffer.add("")
                await buffer.write()
    else:
        buffer.add(helpstring)
        await buffer.write()
