#AkriosMUD

The ultimate goal of AkriosMUD is to provide a Python base with the old school feel
of DIKU derivative MUDs.

Currently AkriosMUD is in an overhaul stage while being converted to use asyncio.  Please
note that this is the game engine.  The engine expects to communicate with a front end / 
proxy which actually accepts and handles the client connections.  The front end created
for the MUD engine can be found here:

https://github.com/bdubyapee/akrios-frontend

## Upcoming changes

As of right now, 5-5-2020, the future plans include:

Complete migration of engine to asyncio.

Revert help files back to JSON files to eliminate dependency on a DB.

Flush out this readme to include instructions on creating keys.py and getting a local
instance running.  Include instructions on using the Grapevine support which is currently
already converted to asyncio.


More updates to follow.

phippsb @ gmail. com

