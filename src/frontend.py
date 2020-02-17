#! usr/bin/env python3
# Project: Dark Waters
# Filename: frontend.py
# 
# File Description: A module to allow connection to the new Akrios Front End.
#
"""
    Module used to communicate with Akrios front end.
"""

# Standard Library
import asyncio
import json
import logging
import websockets
import time

# Third Party

# Project
from keys import FRONT_END
import status

log = logging.getLogger(__name__)

messages_to_frontend = asyncio.Queue()  # String containing JSON
messages_from_frontend = asyncio.Queue()  # String containing JSON
messages_to_game = asyncio.Queue()  # Tuple of (str, str)
commands_to_game = asyncio.Queue()  # Tuple of (str, (options, options))


async def received_heartbeat() -> None:
    """
    Once connected to the front end we will receive regular heartbeats.
    """
    log.info(f'Received heartbeat from frontend at {time.time()}')

    msg = {'event': 'heartbeat',
           'tasks': f'{commands_to_game.empty()}',
           'secret': FRONT_END}

    asyncio.create_task(messages_to_frontend.put(json.dumps(msg, sort_keys=True, indent=4)))


async def received_player_input(payload) -> None:
    """
    We received input from a player.
    """
    uuid = payload['uuid']
    msg = payload['msg']

    log.debug(f"Received front end message: {uuid} '{msg}'")
    asyncio.create_task(messages_to_game.put((uuid, msg)))


async def received_client_connected(payload) -> None:
    """
    We received a notification of a new connection.
    """
    uuid = payload['uuid']
    addr = payload['addr']
    port = payload['port']

    asyncio.create_task(commands_to_game.put(('client_connected', (uuid, addr, port))))


async def received_client_disconnected(payload) -> None:
    """
    We received a notification of a client disconnect.
    """
    uuid = payload['uuid']
    addr = payload['addr']
    port = payload['port']

    asyncio.create_task(commands_to_game.put(('client_disconnected', (uuid, addr, port))))


async def received_game_load_players(payload) -> None:
    """
    We should receive this after a 'softboot'.
    We have notified the front end of a soft boot, it should have restarted us.
    When the game connects to the front end, if there is a list of sessions that means
    we have soft booted, so we're receiving a list of session ID's and player names to log in.
    """
    asyncio.create_task(commands_to_game.put(('game_load_players', payload['players'])))


async def parse_received() -> None:
    rcvr_func = {'heartbeat': received_heartbeat,
                 'player/input': received_player_input,
                 'game/load_players': received_game_load_players,
                 'connection/connected': received_client_connected,
                 'connection/disconnected': received_client_disconnected}

    while status.frontend['connected']:
        message = await messages_from_frontend.get()
        log.info(f'parse_received: {message}')
        message = json.loads(message)
        if 'secret' not in message.keys() or message['secret'] != FRONT_END:
            log.warning('No secret in message header, or wrong key.')
            return
        if message['event'] in rcvr_func:
            if payload := message.get('payload'):
                asyncio.create_task(rcvr_func[message['event']](payload))
            else:
                asyncio.create_task(rcvr_func[message['event']]())


async def ws_read(websocket) -> None:
    while status.frontend['connected']:
        if message := await websocket.recv():
            asyncio.create_task(messages_from_frontend.put(message))
        else:
            status.frontend['connected'] = False


async def ws_write(websocket) -> None:
    while status.frontend['connected']:
        message = await messages_to_frontend.get()
        asyncio.create_task(websocket.send(message))


async def connect() -> None:
    """
    Connect to the front end service.
    Create tasks related to this connection
    """
    async with websockets.connect('ws://localhost:8989') as websocket:
        status.frontend['connected'] = True
        tasks = [asyncio.create_task(parse_received()),
                 asyncio.create_task(ws_read(websocket)),
                 asyncio.create_task(ws_write(websocket))]
        _, pending = await asyncio.wait(tasks, return_when="FIRST_COMPLETED")

    status.frontend['connected'] = False


# Below are helper coroutines to send specific things to the front end.

async def msg_gen_player_output(msg, session_uuid):
    """
    Send output text to a client
    """
    payload = {'message': msg,
               'uuid': session_uuid}
    msg = {'event': 'players/output',
           'secret': FRONT_END,
           'payload': payload}

    asyncio.create_task(messages_to_frontend.put((json.dumps(msg, sort_keys=True, indent=4))))


async def msg_gen_player_login(player_name, uuid_):
    """
    Notify the front end of a successful player login.
    """
    payload = {'name': player_name,
               'uuid': uuid_}
    msg = {'event': 'players/sign-in',
           'secret': FRONT_END,
           'payload': payload}

    asyncio.create_task(messages_to_frontend.put((json.dumps(msg, sort_keys=True, indent=4))))


async def msg_gen_player_logout(player_name, uuid_):
    """
    Notify the front end of a player logout.
    """
    payload = {'name': player_name,
               'message': 'Connection closed',
               'uuid': uuid_}
    msg = {'event': 'players/sign-out',
           'secret': FRONT_END,
           'payload': payload}

    asyncio.create_task(messages_to_frontend.put((json.dumps(msg, sort_keys=True, indent=4))))


async def msg_gen_player_login_failed(player_name, uuid_):
    """
    Notify the front end of a player failed login, "wrong password".
    """
    payload = {'name': player_name,
               'message': 'Connection closed',
               'uuid': uuid_}
    msg = {'event': 'players/login-failed',
           'secret': FRONT_END,
           'payload': payload}

    asyncio.create_task(messages_to_frontend.put((json.dumps(msg, sort_keys=True, indent=4))))


async def msg_gen_game_softboot(wait_time=10):
    """
    Notify the front end the game is going down for softboot.
    """
    payload = {'wait_time': wait_time}
    msg = {'event': 'game/softboot',
           'secret': FRONT_END,
           'payload': payload}

    asyncio.create_task(messages_to_frontend.put((json.dumps(msg, sort_keys=True, indent=4))))


async def msg_gen_player_do_client_echo(uuid_):
    """
    Notify the front end to send a 'do echo' to clients (where appropriate).
    """
    payload = {'command': 'do echo',
               'uuid': uuid_}
    msg = {'event': 'player/session command',
           'secret': FRONT_END,
           'payload': payload}

    asyncio.create_task(messages_to_frontend.put((json.dumps(msg, sort_keys=True, indent=4))))


async def msg_gen_player_dont_client_echo(uuid_):
    """
    Notify the front end to send a 'dont echo' to clients (where appropriate).
    """
    payload = {'command': 'dont echo',
               'uuid': uuid_}
    msg = {'event': 'player/session command',
           'secret': FRONT_END,
           'payload': payload}

    asyncio.create_task(messages_to_frontend.put((json.dumps(msg, sort_keys=True, indent=4))))
