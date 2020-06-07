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
    buffer = outbuffer.OutBuffer(caller)
    
    if args == 'grapevine':
        if caller.oocflags_stored['grapevine'] == 'true':
            caller.oocflags_stored['grapevine'] = 'false'
            buffer.add("\n\r{WGrapevine System disabled.{x")
        else:
            caller.oocflags_stored['grapevine'] = 'true'
            buffer.add("\n\r{WGrapevine System enabled.{x")

    if args == 'ooc':
        if caller.oocflags_stored['ooc'] == 'true':
            caller.oocflags_stored['ooc'] = 'false'
            buffer.add("\n\r{WOOC Channel disabled.{x")
        else:
            caller.oocflags_stored['ooc'] = 'true'
            buffer.add("\n\r{WOOC Channel enabled.{x")

    if args == 'quote':
        if caller.oocflags_stored['quote'] == 'true':
            caller.oocflags_stored['quote'] = 'false'
            buffer.add("\n\r{WQuote Channel disabled.{x")
        else:
            caller.oocflags_stored['quote'] = 'true'
            buffer.add("\n\r{WQuote Channel enabled.{x")

    if args == 'paginate':
        if caller.oocflags_stored['paginate'] == 'true':
            caller.oocflags_stored['paginate'] = 'false'
            buffer.add("\n\r{WPaginate function disabled.{x")
        else:
            caller.oocflags_stored['paginate'] = 'true'
            buffer.add("\n\r{WPaginate function enabled.{x")

    if caller.is_admin:
        if args == 'log debug':
            if logging.getLevelName(logging.root.getEffectiveLevel()) == "INFO":
                logging.root.setLevel("DEBUG")
                log.warning(f"{caller.name.capitalize()} Changed log level to DEBUG")
                buffer.add("\n\r{WSystem level debug has been enabled.{x")
            else:
                logging.root.setLevel("INFO")
                log.warning(f"{caller.name.capitalize()} Changed log level to INFO")
                buffer.add("\n\r{WSystem level debug has been disabled.{x")

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

    if caller.oocflags_stored['paginate'] == 'true':
        paginate_ = "Enabled"
    else:
        paginate_ = "Disabled"

    buffer.add("\n\rCurrently available settings to toggle:")
    buffer.add(f"    {{Wgrapevine{{x : {{R{grapevine_}{{x")
    buffer.add(f"    {{Wooc{{x    : {{R{ooc_}{{x")
    buffer.add(f"    {{Wquote{{x  : {{R{quote_}{{x")
    buffer.add(f"    {{Wpaginate{{x  : {{R{paginate_}{{x")
    buffer.add(f"")
    if caller.is_admin:
        buffer.add(f"    {{Wlog debug{{x : {{R{logging.getLevelName(log.getEffectiveLevel())}{{x")

    await buffer.write()
