#! usr/bin/env python3
# Project: akrios-ii
# Filename: outbuffer.py
#
# File Description: A convenience module to assist with building output buffers to send to clients.
#
"""
    Module used to facilitate centralized output buffer creation.
"""

# Standard Library

# Third Party

# Project


class OutBuffer:
    def __init__(self, caller):
        self.output = []
        self.caller = caller

    def add(self, data):
        self.output.append(data)
        self.output.append('\n\r')

    async def write(self):
        await self.caller.write(f'{"".join(self.output)}')

    def num_lines(self):
        return len(self.output)

    def __repr__(self):
        return f'{"".join(self.output)}\n\r'
