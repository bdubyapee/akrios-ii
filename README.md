#AkriosMUD

The ultimate goal of AkriosMUD is to provide a Python base with the old school feel
of DIKU derivative MUDs.

Currently AkriosMUD is in an overhaul stage while being converted to use asyncio.  Please
note that this is the game engine.  The engine expects to communicate with a front end / 
proxy which actually accepts and handles the client connections.  The front end created
for the MUD engine can be found here:

https://github.com/bdubyapee/akrios-frontend

## Up and running

The game may be in various stages of functionality at any given time during the rewrite.
For now you will need to perform several steps manually to get the game running (in addition to the front end).

##### Create a /players directory under /data
##### Create a keys.py in /src which contains :
     CLIENT_ID which is a str(uuid.uuid4()) for Grapevine
     SECRET_KEY which is a str(uuid.uuid4()) for Grapevine
     FRONT_END which is a str(uuid.uuid4()) for communication with the front end
     
 Please visit https://grapevine.haus for information regarding the Grapevine network.

##### The main launching point is /src/server.py

## Upcoming changes

As of right now, 5-31-2020, the future plans include:

Complete migration of engine to asyncio.

More updates to follow.

phippsb @ gmail. com

