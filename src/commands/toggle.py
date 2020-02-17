#! /usr/bin/env python3
# Project: Akrios
# filename: commands/toggle.py
#
# Capability: player
#
# Command Description: Allows toggling of flags and settings.
#
#
# By: Jubelo

from commands import *
import logging

log = logging.getLogger(__name__)

name = "toggle"
version = 1

requirements = {'capability': ['player', 'mobile'],
                'generic_fail': "See {WHelp toggle{x for help with this command.",
                'truth_checks':  [],
                'false_checks': []}


@Command(**requirements)
async def toggle(caller, args):
    if args == 'grapevine':
        if caller.oocflags_stored['grapevine'] == 'true':
            caller.oocflags_stored['grapevine'] = 'false'
            await caller.write("\n\r{WGrapevine System disabled.{x")
        else:
            caller.oocflags_stored['grapevine'] = 'true'
            await caller.write("\n\r{WGrapevine System enabled.{x")

    if args == 'ooc':
        if caller.oocflags_stored['ooc'] == 'true':
            caller.oocflags_stored['ooc'] = 'false'
            await caller.write("\n\r{WOOC Channel disabled.{x")
        else:
            caller.oocflags_stored['ooc'] = 'true'
            await caller.write("\n\r{WOOC Channel enabled.{x")

    if args == 'quote':
        if caller.oocflags_stored['quote'] == 'true':
            caller.oocflags_stored['quote'] = 'false'
            await caller.write("\n\r{WQuote Channel disabled.{x")
        else:
            caller.oocflags_stored['quote'] = 'true'
            await caller.write("\n\r{WQuote Channel enabled.{x")

    if caller.is_admin:
        if args == 'log debug':
            if logging.getLevelName(logging.root.getEffectiveLevel()) == "INFO":
                logging.root.setLevel("DEBUG")
                log.warning(f"{caller.name.capitalize()} Changed log level to DEBUG")
                await caller.write("\n\r{WSystem level debug has been enabled.{x")
            else:
                logging.root.setLevel("INFO")
                log.warning(f"{caller.name.capitalize()} Changed log level to INFO")
                await caller.write("\n\r{WSystem level debug has been disabled.{x")

    if caller.oocflags_stored['grapevine'] == 'true':
        grapevine_ = "Enabled"
    else:
        grapevine_ = "Disabled"

    if caller.oocflags_stored['ooc'] == 'true':
        ooc_ = "Enabled"
    else:
        ooc_ = "Disabled"

    if caller.oocflags_stored['quote'] == 'true':
        quote_ = "Enabled"
    else:
        quote_ = "Disabled"

    await caller.write("\n\rCurrently available settings to toggle:")
    await caller.write(f"    {{Wgrapevine{{x : {{R{grapevine_}{{x")
    await caller.write(f"    {{Wooc{{x    : {{R{ooc_}{{x")
    await caller.write(f"    {{Wquote{{x  : {{R{quote_}{{x")
    await caller.write(f"")
    if caller.is_admin:
        await caller.write(f"    {{Wlog debug{{x : {{R{logging.getLevelName(log.getEffectiveLevel())}{{x")
