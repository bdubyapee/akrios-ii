# Project: Akrios
# Filename: commands/raceslist.py
#
# Capability: builder
#
# Command Description: Provides a list of all of the races for builders as a reference.
#
# By: Jubelo

from commands import *

name = "raceslist"
version = 1

requirements = {'capability': ['builder'],
                'generic_fail': "See {WHelp raceslist{x for help with this command.",
                'truth_checks':  [],
                'false_checks': []}


@Command(**requirements)
async def raceslist(caller, args, **kwargs):
    buffer = outbuffer.OutBuffer(caller)

    buffer.add("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=Races=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-")
    buffer.add("")

    race_names = [each_race.capitalize() for each_race in races.racesdict.keys()]
    race_names.sort()
    numcols = 6
    while (len(race_names) % numcols) > 0:
        race_names.append(' ')
    for i in range(0, len(race_names), numcols):
        output = ''
        for l in range(0, numcols):
            output = f"{output}{race_names[i+l]:12}"
        buffer.add(output)

    await buffer.write()

