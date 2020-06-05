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
    buffer = outbuffer.OutBuffer(caller)

    if caller.oocflags_stored['grapevine'] == 'false':
        buffer.add("You have Grapevine disabled with the 'toggle' command.")
        await buffer.write()
        return

    if args == '':
        akrios_subscribed = []
        for chan, subbed in grapevine.subscribed.items():
            if subbed:
                akrios_subscribed.append(chan)

        buffer.add(f"Akrios subscribed to: {', '.join(akrios_subscribed)}.")
        buffer.add(f"You are subscribed to: {', '.join(caller.oocflags['grapevine_channels'])}.")
        await buffer.write()
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
            buffer.add(f"Sending unsubscribe to Grapevine for channel: {channel}")
            await buffer.write()
            return
        else:
            asyncio.create_task(grapevine.msg_gen_chan_subscribe(channel))
            buffer.add(f"Sending subscribe to Grapevine for channel: {channel}")
            await buffer.write()
            return

    if channel in grapevine.subscribed:
        if channel in caller.oocflags['grapevine_channels']:
            buffer.add(f"You are already subscribed to channels: {caller.oocflags['grapevine_channels']}.")
            await buffer.write()
            return
        else:
            caller.oocflags['grapevine_channels'].append(channel)
            buffer.add(f"Subscribing you to {channel}")
            await buffer.write()
    else:
        buffer.add("Akrios is not subscribed to that Grapevine channel.  Ask Jubelo to subscribe.")
        await buffer.write()
