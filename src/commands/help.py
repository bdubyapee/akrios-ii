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
        if ' ' in key:
            key = key.split()[0]
        await caller.sock.query_db('help', key)
        await caller.sock.send_prompt()
    else:
        header = f"{{rHelp Files by Topic{{x"
        await caller.write(f"{header:^80}")

        result = await caller.sock.query_db('help keywords')

        log.debug(f'HELP RESULT: {result}')

        topics = {}
        for keyword, section, topic in result:
            if topic in topics:
                topics[topic].append(keyword[0])
            else:
                topics[topic] = keyword

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
