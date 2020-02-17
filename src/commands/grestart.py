#! usr/bin/env python3
# Project: Akrios
# filename: commands/grestart.py
#
# Capability : admin
#
# Command Description: This command simulates a restart received from grapevine.
#
#
#
# By: Jubelo

from commands import *
import grapevine

name = "grestart"
version = 1

requirements = {'capability': ['admin'],
                'generic_fail': "See {WHelp grestart{x for help with this command.",
                'truth_checks':  [],
                'false_checks': []}


@Command(**requirements)
async def grestart(caller, args, **kwargs):
    await player.wiznet("Initiating restart simulation from Grapevine.")

    payload = {"downtime": 15}

    package = {"event": "restart",
               "ref": str(uuid.uuid4()),
               "payload": payload}

    jsonified = json.dumps(package, sort_keys=True, indent=4)

    asyncio.create_task(grapevine.messages_from_grapevine.put(jsonified))
    
    await player.wiznet("Created fake restart JSON payload and appended to socket in buffer")
