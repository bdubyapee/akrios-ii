# Project: Akrios
# Filename: commands/commandlist.py
#
# Capability: player
#
# Command Description: Listing of currently available commands filtered by capabilities.
#
# By: Jubelo

from commands import *

name = "commandslist"
version = 1

requirements = {'capability': ['player'],
                'generic_fail': "See {WHelp commandlist{x for help with this command.",
                'truth_checks':  [],
                'false_checks': []}


@Command(**requirements)
async def commandslist(caller, args, **kwargs):
    buffer = outbuffer.OutBuffer(caller)
    header = f"{{rCommands Available{{x"

    buffer.add(f"{header:^80}")
    buffer.add("")
    sub_header = f"{{BPlease see {{Whelp <command>{{B for additional information{{x"
    buffer.add(f"{sub_header:^80}")
    buffer.add("")

    cmd_list = [cmd for cmd in Command.commandhash
                if set(Command.commandcapability[cmd]) & set(caller.capability)]
    
    cmd_list.sort()
    numcols = 4
    while (len(cmd_list) % numcols) > 0:
        cmd_list.append(' ')
    for i in range(0, len(cmd_list), numcols):
        output = ''
        for l in range(0, numcols):
            output = f"{output}{cmd_list[i+l]:20}"
        buffer.add(output)

    buffer.add("")
    buffer.add("\n\r{WUsage{x: <command> <optional arguments>")
    await buffer.write()
