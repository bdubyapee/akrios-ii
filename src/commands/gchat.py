#! /usr/bin/env python3
# Project: Akrios
# Filename: commands/gchat.py
#
# Capability: player
#
# Command Description: This is the Out of Character (OOC) chat command. It goes
# to the Grapevine MUD Chat Network.
#
# By: Jubelo

from commands import *
import grapevine

name = "gchat"
version = 1

requirements = {'capability': ['player'],
                'generic_fail': "See {WHelp gchat{x for help with this command.",
                'truth_checks':  ['args_required'],
                'false_checks': []}


@Command(**requirements)
async def gchat(caller, args, **kwargs):
    if caller.oocflags_stored['grapevine'] == 'false':
        await caller.write("You have Grapevine disabled with the 'toggle' command.")
        return

    channel, msg = args.split()
    channel = channel.lower()

    if channel not in grapevine.subscribed:
        await caller.write("Channel not subscribed.\n\r{Wgchat <channel> <message>{x")
        await caller.write(f"Subscribed channels are: {grapevine.subscribed}")
        return

    try:
        asyncio.create_task(grapevine.msg_gen_message_channel_send(caller, channel, msg))
    except:
        await caller.write(f"{{WError chatting to Grapevine Network, try again later{{x")
        log.warning(f"Error writing to Grapevine network. {caller.disp_name} : {msg}")
        return
    
    await caller.write(f"{{GYou Grapevine {{B{channel}{{G chat{{x: '{{G{msg}{{x'")

    for eachplayer in player.playerlist:
        if eachplayer.oocflags_stored['grapevine'] == 'true' and eachplayer.aid != caller.aid:
            await eachplayer.write(f"\n\r{{G{caller.disp_name} Grapevine {{B{channel}{{G chats{{x: '{{G{msg}{{x'")


