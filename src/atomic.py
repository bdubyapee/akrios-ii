#! usr/bin/env python
# Project: Akrios
# Filename: atomic.py
# 
# File Description: The atomic module.  House anything that will pertain to all
#                   players, mobiles and objects.
# 
# By: Jubelo

# Imports here
import logging
import time

import area
import comm
import commands
import exits
import helpsys
import races
import room

log = logging.getLogger(__name__)


class Atomic(object):
    def __init__(self):
        super().__init__()
        self.alias = {}
        # self.building = None
        self.capability = []
        # self.editing = None
        self.location = None
        self.last_input = 0
        self.name = ''
        self.oocflags = {}
        self.short_description = ''
        self.snooped_by = []
        self.sock = None

    async def write(self, *args, **kwargs):
        pass

    async def interp(self, inp=None, forced=False):

        if self.snooped_by:
            for each_person in self.snooped_by:
                each_person.write(f"{self.name} typed: {inp}")

        inp = inp.split()

        if self.is_player:
            self.oocflags['afk'] = False
            self.last_input = time.time()

        if self.is_player and self.oocflags['is_paginating']:
            log.debug(f'Inside interp: we are paginating. inp is {inp}')
            if not inp or inp[0] != 'q':
                output, self.sock.page_buf = self.sock.page_buf[:self.sock.rows], self.sock.page_buf[self.sock.rows:]
                await self.write(''.join(output))
                if len(self.sock.page_buf) <= 0:
                    self.oocflags['is_paginating'] = False
                await self.sock.send_prompt()
            else:
                self.sock.page_buf = []
                self.oocflags['is_paginating'] = False
                await self.write('')
                await self.sock.send_prompt()
            return

        is_building = hasattr(self, 'building')
        is_editing = hasattr(self, 'editing')

        if not inp:
            if is_building and not is_editing:
                await self.write(self.building.display())
                return
            if is_editing:
                self.editing.add('')
                return
            else:
                await self.sock.send_prompt()
                return

        # Look in living thing command alias dict, swap alias for full command if found        
        if inp[0] in self.alias:
            inp[0] = self.alias[inp[0]]

        # Added some time ago for OLC to work properly.  Fix this XXX
        if not inp:
            inp = ['']

        comfind = []

        for item in sorted(commands.Command.commandhash):
            if item.startswith(inp[0].lower()):
                comfind.append(commands.Command.commandhash[item])

        if is_building:
            types = {helpsys.Help: 'helpedit',
                     races.Race: 'raceedit',
                     area.Area: 'areaedit',
                     room.Room: 'roomedit',
                     exits.Exit: 'exitedit'}
            if self.building.__class__ in types:
                comfind.append(commands.Command.commandhash[types[self.building.__class__]])
                # If the person is building we prepend the command they are using.
                inp.insert(0, types[self.building.__class__])
                await self.write('')

        if comfind:
            try:
                if is_editing:
                    await comfind[-1](self, ' '.join(inp[1:]))
                elif is_building:
                    if comfind[0].__name__ not in types.values():
                        await comfind[0](self, ' '.join(inp[2:]))
                    else:
                        await comfind[0](self, ' '.join(inp[1:]))
                else:
                    await self.write('')
                    await comfind[0](self, ' '.join(inp[1:]))
                    if self.is_player and not forced:
                        await self.sock.send_prompt()
            except (NameError, IndexError) as msg:
                await self.write(msg)
        else:
            await self.write("Huh?")

    async def move(self, tospot=None, fromspot=None, direction=None):
        rev_direction = "the ether"

        if tospot is None:
            log.warning("Received None value in move method")
            return

        mover = self.disp_name

        if direction is None:
            rev_direction = "the ether"
        elif direction != "goto":
            rev_direction = exits.oppositedirection[direction]

        if fromspot is not None:
            if direction == "goto":
                fromspot_message = f"{mover} has vanished into thin air."
            else:
                fromspot_message = f"{mover} has left to the {direction}."
            await comm.message_to_room(fromspot, self, fromspot_message)
            fromspot.contents.remove(self)

        # Once object notification is in, notify left room of departure and
        # room we moved to of arrival.

        tospot.contents.append(self)
        self.location = tospot

        if direction == "goto" or fromspot is None:
            tospot_message = f"{mover} has sprung into existence!"
        else:
            tospot_message = f"{mover} has arrived from the {rev_direction}."
        await comm.message_to_room(tospot, self, tospot_message)

    def capability_contains(self, capability=''):
        return True if capability and capability in self.capability else False

    @property
    def is_admin(self):
        return self.capability_contains('admin')

    @property
    def is_deity(self):
        return self.capability_contains('deity')

    @property
    def is_builder(self):
        return self.capability_contains('builder')

    @property
    def is_player(self):
        return self.capability_contains('player')

    @property
    def is_mobile(self):
        return self.capability_contains('mobile')

    @property
    def is_object(self):
        return self.capability_contains('object')

    @property
    def disp_name(self):
        return self.name.capitalize() if self.is_player else self.short_description
