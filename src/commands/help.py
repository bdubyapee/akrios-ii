#! usr/bin/env python3
# Project: Akrios
# filename: commands/help.py
#
# Capability: player
#
# Command Description: The main help command in the game.
#
# By: Jubelo

from commands import *

name = "help"
version = 1

requirements = {'capability': ['player'],
                'generic_fail': "See {WHelp{x for help with this command.",
                'truth_checks':  [],
                'false_checks': []}


@Command(**requirements)
async def help(caller, args, **kwargs):
    key = args.lower()
    if key != '':
        key = key.split()
        for onekey in helpsys.helpfiles:
            if onekey.startswith(key[0]):
                if helpsys.helpfiles[onekey].viewable.lower() == 'true':
                    caller.write(helpsys.helpfiles[onekey].description)
                    return
        filename = os.path.join(world.logDir, 'missinghelp')
        with open(filename, 'a') as thefile:
            thefile.write(f'{time.asctime()}> {key}\n')
        await caller.write('We do not appear to have a help file for that topic.  We have however logged'
                           ' the attempt and will look into creating a help file for that topic.')
    else:
        header = f"{{rHelp Files by Topic{{x"
        await caller.write(f"{header:^80}")

        retval = []
        for onehelp in helpsys.helpfiles:
            if helpsys.helpfiles[onehelp].viewable.lower() == 'true':
                if helpsys.helpfiles[onehelp].section in caller.capability:
                    retval.append(onehelp)

        # Create a dict of topics, each has a list value.
        topics = {}
        # Append each help keywords under the section.
        for eachhelp in retval:
            if helpsys.helpfiles[eachhelp].topics in topics:
                topics[helpsys.helpfiles[eachhelp].topics].append(eachhelp)
            else:
                topics[helpsys.helpfiles[eachhelp].topics] = [eachhelp]

        topics_sorted = list(topics)
        topics_sorted.sort()

        # Then build the Cols list per topic and display.
        for eachtopic in topics_sorted:
            if eachtopic == "game, rp, mythos":
                temp_topic = "Game, RP, Mythos"
                await caller.write(f"\n\r{{B{temp_topic:^77}{{x")
            else:
                await caller.write(f"\n\r{{B{eachtopic.capitalize():^77}{{x")

            the_keywords = topics[eachtopic]
            the_keywords.sort()

            numcols = 4
            while (len(the_keywords) % numcols) > 0:
                the_keywords.append(' ')
            for i in range(0, len(the_keywords), numcols):
                output = ''
                for l in range(0, numcols):
                    output = f"{output}{the_keywords[i+l]:20}"
                await caller.write(output)
        await caller.write("\n\r\n\r{WUsage{x: help <argument>\n\r")
