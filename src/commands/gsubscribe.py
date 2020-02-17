#! /usr/bin/env python3
# Project: Akrios
# Filename: commands/gsubscribe.py
#
# Capability: player
#
# Command Description: Used to subscribe or unsubscribe from Grapevine Channels.
#
# By: Jubelo

from commands import *
import grapevine

name = "gsubscribe"
version = 1

requirements = {'capability': ['player'],
                'generic_fail': "See {WHelp gsubscribe{x for help with this command.",
                'truth_checks':  [],
                'false_checks': []}


@Command(**requirements)
async def gsubscribe(caller, args='', **kwargs):
    if caller.oocflags_stored['grapevine'] == 'false':
        await caller.write("You have Grapevine disabled with the 'toggle' command.")
        return

    if args == '':
        akrios_subscribed = []
        for chan, subbed in grapevine.subscribed.items():
            if subbed:
                akrios_subscribed.append(chan)

        await caller.write(f"Akrios subscribed to: {', '.join(akrios_subscribed)}.")
        await caller.write(f"You are subscribed to: {', '.join(caller.oocflags['grapevine_channels'])}.")
        return

    if ' ' in args:
        channel, force_ = args.split()
        channel = channel.lower()
        force_ = force_.lower()
    else:
        channel = args.lower()
        force_ = ''

    if caller.is_admin and force_ == 'force':
        if channel in grapevine.subscribed:
            asyncio.create_task(grapevine.msg_gen_chan_unsubscribe(channel))
            await caller.write(f"Sending unsubscribe to Grapevine for channel: {channel}")
            return
        else:
            asyncio.create_task(grapevine.msg_gen_chan_subscribe(channel))
            await caller.write(f"Sending subscribe to Grapevine for channel: {channel}")
            return

    if channel in grapevine.subscribed:
        if channel in caller.oocflags['grapevine_channels']:
            await caller.write(f"You are already subscribed to channels: {caller.oocflags['grapevine_channels']}.")
            return
        else:
            caller.oocflags['grapevine_channels'].append(channel)
            await caller.write(f"Subscribing you to {channel}")
    else:
        await caller.write("Akrios is not subscribed to that Grapevine channel.  Ask Jubelo to subscribe.")
