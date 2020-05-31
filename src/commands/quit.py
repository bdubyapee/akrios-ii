#! usr/bin/env python3
# Project: Akrios
# filename: commands/quit.py
#
# Capability : player
#
# Command Description: The quit command for players.
#
# By: Jubelo

from commands import *
import login

name = 'quit'
version = 1

requirements = {'capability': ['player'],
                'generic_fail': "See {WHelp quit{x for help with this command.",
                'truth_checks':  [],
                'false_checks': []}


@Command(**requirements)
async def quit(caller, args, **kwargs):
    if caller.is_building or caller.is_editing: 
        await caller.write("You must finish building first!")
        return

    caller.save()
    caller.location.contents.remove(caller)
    caller.sock.promptable = False
    caller.sock.state['logged in'] = False
    conn = login.Login(caller.name)
    testsock = caller.sock

    if caller in player.playerlist:
        player.playerlist.remove(caller)
    if caller.name in player.playerlist_by_name:
        player.playerlist_by_name.pop(caller.name)
    if caller.aid in player.playerlist_by_aid:
        player.playerlist_by_aid.pop(caller.aid)
    if args == "force":
        reason = "[FORCED] "
    else:
        reason = ""

    await player.wiznet(f"{reason}{caller.name} logging out of Akrios.")

    conn.sock = testsock
    conn.sock.owner = conn
    if 'force' not in args:
        await conn.main_menu()
    # Linkdeath/timeout will force a quit.  Test for that below so we remove
    # them completely from the game and don't leave them stuck at the menu.
    if args == "force":
        await conn.main_menu_get_option('l')
    elif args == "force no_notify":
        await conn.main_menu_get_option('l no_notify')
    else:
        conn.interp = conn.main_menu_get_option
