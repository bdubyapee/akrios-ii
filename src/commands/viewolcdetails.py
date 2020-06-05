# Project: Akrios
# filename: commands/viewolcdetails.py
#
# Capabilities: builder
#
# Command Description: This flag turns on and allows the builder+ capability user to see inline details.
#
# By: Jubelo

from commands import *

name = "viewolcdetails"
version = 1

requirements = {'capability': ['builder'],
                'generic_fail': "See {WHelp viewolcdetails{x for help with this command.",
                'truth_checks':  [],
                'false_checks': []}


@Command(**requirements)
async def viewolcdetails(caller, args, **kwargs):
    buffer = outbuffer.OutBuffer(caller)

    if caller.oocflags['viewOLCdetails'] is True:
        caller.oocflags['viewOLCdetails'] = False
        buffer.add("You will no longer see OLC details.")
    else:
        caller.oocflags['viewOLCdetails'] = True
        buffer.add("You will now see OLC details.")

    await buffer.write()

