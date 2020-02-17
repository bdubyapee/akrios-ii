#! usr/bin/env python3
# Project: Akrios
# Filename: grapevine.py
# 
# File Description: A module to allow connection to Grapevine chat network.
#                   Visit https://www.grapevine.haus/
#
# Implemented features:
#       Authentication to the grapevine network.
#       Registration to the Gossip Channel(default) or other channels.
#       Restart messages from the grapevine network.
#       Sending and receiving messages to the Gossip(default) or other channel.
#       Sending and receiving Player sign-in/sign-out messages.
#       Player sending and receiving Tells.
#       Sending and receiving player status requests.
#       Sending single game requests.
#       Game connect and disconnect messages.
#       Sending and receiving game status requests.
#       Game Status (all connected games, and single game)
#       Achievements (Sync, Creation, update, deletion)
#
#
# Or visit the latest version of the live client at:
# https://github.com/bdubyapee/akriosmud
#
# By: Jubelo, Creator of AkriosMUD
# At: akriosmud.funcity.org:5678
#     jubelo@akriosmud.funcity.org
# 

"""
    Module used to communicate with the Grapevine.haus chat+ network.
    https://grapevine.haus
    https://vineyard.haus

"""

import asyncio
import datetime
import json
import logging
import time
from typing import Tuple
import uuid
import websockets

from keys import CLIENT_ID, SECRET_KEY
import player
import status

log = logging.getLogger(__name__)

messages_to_grapevine = asyncio.Queue()
messages_from_grapevine = asyncio.Queue()
messages_to_game = asyncio.Queue()


supports = ['channels', 'games', 'players', 'tells']

# Populate the channels attribute if you want to subscribe to a specific
# channel or channels during authentication.
channels = ['gossip']
version = '2.3.0'
user_agent = 'AkriosMUD v0.4.5'

subscribed = {'gossip': True}

sent_refs = {}

# The below is a cache of players we know about from other games.
# Right now I just use this to populate additional fields in our in-game 'who' command
# to also show players logged into other Grapevine connected games.
other_games_players = {}

inner_values = {'restart_downtime': 0,
                'total_achievements': 0,
                'last_heartbeat': 0.0,
                'achievements': {}}


def is_event_status(message, status_):
    """
        A helper method to determine if the event we received is type of status.

        return True/False
    """
    if 'event' in message and 'status' in message:
        if message['status'] == status_:
            return True
        else:
            return False


async def received_heartbeat(message) -> None:
    last_heartbeat = time.time()
    log.debug(f'Received heartbeat from grapevine at {last_heartbeat}')
    inner_values['last_heartbeat'] = last_heartbeat
    asyncio.create_task(msg_gen_heartbeat())
    

async def received_auth(message) -> None:
    """
        We received an event Auth event type.
        Determine if we are already authenticated, if so subscribe to the channels
        as determined in msg_gen_chan_subscribed in the GrapevineSocket Object.
        Otherwise, if we are not authenticated yet we send another authentication attempt
        via msg_gen_authenticate().  This is in place for path hiccups or restart events.

        Grapevine 1.0.0
    """
    if is_event_status(message, 'success'):
        status.grapevine['authenticated'] = True
        status.grapevine['connected'] = True
        asyncio.create_task(msg_gen_chan_subscribe())
        log.info('Received authentication success from Grapevine.')
        asyncio.create_task(msg_gen_player_status_query())
        log.info('Sending player status query to all Grapevine games.')
    elif not status.grapevine['authenticated']:
        log.info('received_auth: Sending Authentication message to Grapevine.')
        asyncio.create_task(msg_gen_authenticate())


async def received_restart(message) -> None:
    """
    We received a restart event. We'll assign the value to the restart_downtime
    attribute for access by the calling code.

    Grapevine 1.0.0
    """
    if 'payload' in message:
        inner_values['restart_downtime'] = int(message['payload']['downtime'])


async def received_chan_sub(message, sent_refs_) -> None:
    """
    We have attempted to subscribe to a channel.  This is a response message from Grapevine.
    If failure, we make sure we show unsubscribed in our local list.
    if success, we make sure we show subscribed in our local list.

    Grapevine 1.0.0
    """
    if 'ref' in message and message['ref'] in sent_refs_:
        orig_req = sent_refs_.pop(message['ref'])
        if is_event_status(message, 'failure'):
            channel = orig_req['payload']['channel']
            subscribed[channel] = False
            log.warning(f"Grapevine failed to subscribe to channel {channel}")
        elif is_event_status(message, 'success'):
            channel = orig_req['payload']['channel']
            subscribed[channel] = True
            log.info(f"Grapevine successfully subscribed to channel {channel}")


async def received_chan_unsub(message, sent_refs_) -> None:
    """
    We at some point sent a channel unsubscribe. This is verifying Grapevine
    received that.  We unsub in our local list.

    Grapevine 1.0.0
    """
    if 'ref' in message and message['ref'] in sent_refs_:
        orig_req = sent_refs_.pop(message['ref'])
        channel = orig_req['payload']['channel']
        subscribed[channel] = False
        log.info(f"Grapevine unsubscribed from channel {channel}")


async def received_player_logout(message, sent_refs_) -> Tuple:
    """
    We have received a "player/sign-out" message from Grapevine.

    Determine if it is a success message, which is an indication to us that Grapevine
    received a player logout from us and is acknowledging, or if it is a message from
    another game on the Grapevine network.

    return None if it's an ack from grapevine, return player info if it's foreign.

    Grapevine 1.0.0
    """
    if 'ref' in message:
        # We are a success message from Grapevine returned from our notification.
        if message['ref'] in sent_refs_ and is_event_status(message, 'success'):
            sent_refs_.pop(message['ref'])
            return
        # We are receiving a player logout from another game.
        if 'game' in message['payload']:
            game = message['payload']['game'].capitalize()
            player_ = message['payload']['name'].capitalize()
            if game in other_games_players:
                if player_ in other_games_players[game]:
                    other_games_players[game].remove(player_)
                if len(other_games_players[game]) <= 0:
                    other_games_players.pop(game)

            return 'player/logout', f'{player_} signed out of {game}'


async def received_player_login(message, sent_refs_) -> Tuple:
    """
    We have received a "player/sign-in" message from Grapevine.

    Determine if it is a success message, which is an indication to us that Grapevine
    received a player login from us and is acknowledging, or if it is a message from
    another game on the Grapevine Network.

    return None if it's an ack from grapevine, return player info if it's foreign

    Grapevine 1.0.0
    """
    if 'ref' in message:
        if message['ref'] in sent_refs_ and is_event_status(message, 'success'):
            sent_refs_.pop(message['ref'])
            return
        if 'game' in message['payload']:
            game = message['payload']['game'].capitalize()
            player_ = message['payload']['name'].capitalize()
            if game in other_games_players:
                if player_ not in other_games_players[game]:
                    other_games_players[game].append(player_)
            else:
                other_games_players[game] = []
                other_games_players[game].append(player_)

            return 'player/logout', f'{player_} signed into {game}'


async def received_player_status(message, sent_refs_) -> None:
    """
    We have requested a multi-game or single game status update.
    This is the response. We pop the valid Ref from our local list
    and add them to the local cache.

    Grapevine 1.1.0
    """
    if 'ref' in message and 'payload' in message:
        # On first receive we pop the ref just so it's gone from the queue
        if message['ref'] in sent_refs_:
            sent_refs_.pop(message['ref'])

        game = message['payload']['game'].capitalize()

        if len(message['payload']['players']) == 1 and message['payload']['players'] in ['', None]:
            other_games_players[game] = []
        if len(message['payload']['players']) == 1:
            player_ = message['payload']['players'][0].capitalize()
            other_games_players[game] = []
            other_games_players[game].append(player_)
        if len(message['payload']['players']) > 1:
            player_ = [player_.capitalize() for player_ in message['payload']['players']]
            other_games_players[game] = []
            other_games_players[game] = player_


async def received_tells_status(message, sent_refs_) -> Tuple:
    """
    One of the local players has sent a tell.  This is specific response of an error.
    Provide the error and other pertinent info to the local game for handling
    as required.

    Grapevine 2.0.0
    """
    if 'ref' in message:
        if message['ref'] in sent_refs_ and 'error' in message:
            orig_req = sent_refs_.pop(message['ref'])
            if is_event_status(message, 'failure'):
                caller = orig_req['payload']['from_name'].capitalize()
                target = orig_req['payload']['to_name'].capitalize()
                game = orig_req['payload']['to_game'].capitalize()
                
                return 'tells/send', (caller, target, game, message['error'])


async def received_tells_message(message) -> Tuple:
    """
    We have received a tell message destined for a player in our game.
    Grab the details and return to the local game to handle as required.

    Grapevine 2.0.0
    """
    if 'ref' in message and 'payload' in message:
        sender = message['payload']['from_name']
        target = message['payload']['to_name']
        game = message['payload']['from_game']
        sent = message['payload']['sent_at']
        message = message['payload']['message']

        log.info(f"Grapevine received tell: {sender}@{game} told {target} '{message}'")
        
        return 'tells/receive', (sender, target, game, sent, message)


async def received_games_status(message, sent_refs_) -> Tuple:
    """
    Received a game status response.  Return the received info to the local
    game to handle as required.

    Grapevine 2.1.0
    """
    if 'ref' in message and 'payload' in message and is_event_status(message, "success"):
        sent_refs_.pop(message['ref'])
        if message['ref'] in sent_refs_:
            game = message['payload']['game']
            display_name = message['payload']['display_name']
            description = message['payload']['description']
            homepage = message['payload']['homepage_url']
            user_agent_ = message['payload']['user_agent']
            user_agent_repo = message['payload']['user_agent_repo_url']
            connections = message['payload']['connections']

            supports_ = message['payload']['supports']
            num_players = message['payload']['players_online_count']

            return (game, display_name, description, homepage, user_agent_,
                    user_agent_repo, connections, supports_, num_players)

    if 'ref' in message and 'error' in message and is_event_status(message, 'failure'):
        orig_req = sent_refs_.pop(message['ref'])
        if message['ref'] in sent_refs_:
            game = orig_req['payload']['game']
            return game, message['error']


async def received_message_confirm(message, sent_refs_) -> None:
    """
    We received a confirmation that Grapevine received an outbound broadcast message
    from us.  Nothing to see here other than removing from our sent references list.

    Grapevine : Should be semi version neutral.
    """
    if 'ref' in message:
        if message['ref'] in sent_refs_ and is_event_status(message, 'success'):
            sent_refs_.pop(message['ref'])


def is_other_game_player_update(message) -> bool:
    """
    A helper method to determine if this is a player update from another game.
    """
    if 'event' in message:
        if message['event'] == 'players/sign-in' or message['event'] == 'players/sign-out':
            if 'payload' in message and 'game' in message['payload']:
                return True
        else:
            return False


async def received_games_connected(message) -> Tuple:
    """
    A foreign game has connected to the network, add the game to our local
    cache of games/players and send a request for player list.

    Grapevine 2.2.0
    """
    if 'payload' in message:
        # Clear what we knew about this game and request an update.
        # Requesting updates from all games at this point, might as well refresh
        # as I'm sure some games don't implement all features like player sign-in
        # and sign-outs.
        other_games_players[message['payload']['game']] = []
        asyncio.create_task(msg_gen_player_status_query())
        return 'games/connect', (message['payload']['game'])


async def received_games_disconnected(message) -> Tuple:
    """
    A foreign game has disconnected, remove it from our local cache and return
    details to local game to handle as required.

    Grapevine 2.2.0
    """
    if 'payload' in message:
        if message['payload']['game'] in other_games_players:
            other_games_players.pop(message['payload']['game'])
        return 'games/disconnect', (message['payload']['game'])


async def received_broadcast_message(message) -> Tuple:
    """
    We received a broadcast message from another game.  Return the pertinent
    info so the local game can handle as required.  See examples above.

    Grapevine 1.0.0
    """
    if 'payload' in message:
        name = message['payload']['name']
        game = message['payload']['game']
        message = message['payload']['message']
        channel = message['payload']['channel']

        log.info(f"Grapevine received message: {name}@{game} on {channel} said '{message}'")
        return 'channels/broadcast', (name, game, message, channel)


async def received_achievements_sync(message, sent_refs_) -> None:
    """
    We have received an achievements sync response.
    Grab the details and update the achievements attribute.

    Grapevine 2.3.0
    """
    if 'ref' in message and 'payload' in message:
        if message['ref'] in sent_refs_:
            sent_refs_.pop(message['ref'])
        # total_achievements = message['payload']['total']
        all_achievements = message['payload']['achievements']

        for each_achievement in all_achievements:
            inner_values['achievements'][each_achievement['key']] = each_achievement


async def received_achievements_create(message, sent_refs_) -> None:
    """
    We have received an achievements create response.
    Grab the details and update the achievements attribute.

    Grapevine 2.3.0
    """
    if 'ref' in message and 'payload' in message and 'status' in message:
        if message['ref'] in sent_refs_:
            sent_refs_.pop(message['ref'])
        if message['status'] == 'success':
            if message['payload']['key'] not in inner_values['achievements']:
                inner_values['achievements']['key'] = message['payload']
                return
        elif message['status'] == 'failure':
            return message['payload']['errors']


async def received_achievements_update(message, sent_refs_) -> None:
    """
    We have received an achievements update response.
    Grab the details and update the achievements attribute.

    Grapevine 2.3.0
    """
    if 'ref' in message and 'payload' in message and 'status' in message:
        if message['ref'] in sent_refs_:
            sent_refs_.pop(message['ref'])
        if message['status'] == 'success':
            if message['payload']['key'] not in inner_values['achievements']:
                inner_values['achievements']['key'] = message['payload']
                return
        elif message['status'] == 'failure':
            return message['payload']['errors']


async def received_achievements_delete(message, sent_refs_) -> None:
    """
    We have received an achievements update response.
    Grab the details and update the achievements attribute.

    Grapevine 2.3.0
    """
    if 'ref' in message and 'payload' in message and 'status' in message:
        if message['ref'] in sent_refs_:
            sent_refs_.pop(message['ref'])
        if message['status'] == 'success':
            key = message['payload']['key']
            if key in inner_values['achievements']:
                inner_values['achievements'][key].pop(key)


async def parse_received() -> None:
    rcvr_func = {'heartbeat': (received_heartbeat, None),
                 'authenticate': (received_auth, None),
                 'restart': (received_restart, None),
                 'channels/broadcast': (received_broadcast_message, None),
                 'channels/subscribe': (received_chan_sub, sent_refs),
                 'channels/unsubscribe': (received_chan_unsub, sent_refs),
                 'players/sign-out': (received_player_logout, sent_refs),
                 'players/sign-in': (received_player_login, sent_refs),
                 'games/connect': (received_games_connected, None),
                 'games/disconnect': (received_games_disconnected, None),
                 'games/status': (received_games_status, sent_refs),
                 'players/status': (received_player_status, sent_refs),
                 'tells/send': (received_tells_status, sent_refs),
                 'tells/receive': (received_tells_message, None),
                 'channels/send': (received_message_confirm, sent_refs),
                 'achievements/sync': (received_achievements_sync, sent_refs),
                 'achievements/create': (received_achievements_create, sent_refs),
                 'achievements/update': (received_achievements_update, sent_refs),
                 'achievements/delete': (received_achievements_delete, sent_refs)}

    while status.grapevine['connected']:
        message = await messages_from_grapevine.get()
        message = json.loads(message)
        log.debug(f'Message received from Grapevine: {message}')
        if 'event' in message and message['event'] in rcvr_func:
            exec_func, args = rcvr_func[message['event']]
            if args is None:
                response = await exec_func(message)
            else:
                response = await exec_func(message, args)
            if response:
                log.info(f'grapevine.parse_rcvd response is: {response}')
                asyncio.create_task(messages_to_game.put(response))


async def read(websocket) -> None:
    while status.grapevine['connected']:
        if message := await websocket.recv():
            asyncio.create_task(messages_from_grapevine.put(message))
        else:
            status.grapevine['connected'] = False


async def write(websocket) -> None:
    while status.grapevine['connected']:
        message = await messages_to_grapevine.get()
        asyncio.create_task(websocket.send(message))


async def connect() -> None:
    """
    Connect to the Grapevine service.
    Create tasks related to this connection
    """
    while status.server['running']:
        async with websockets.connect('wss://grapevine.haus/socket') as websocket:
            log.info('Run of grapevine connect')
            asyncio.create_task(msg_gen_authenticate())
            status.grapevine['connected'] = True
            tasks = [asyncio.create_task(parse_received()),
                     asyncio.create_task(read(websocket)),
                     asyncio.create_task(write(websocket))]
            completed, pending = await asyncio.wait(tasks, return_when="FIRST_COMPLETED")

        log.info('Shutting down Grapevine connection.')
        log.info(f'Grapevine completed task: {completed}\n\r')
        status.grapevine['connected'] = False
        subscribed.clear()
        other_games_players.clear()


async def msg_gen_authenticate() -> None:
    """
    Need to authenticate to the Grapevine.haus network to participate.
    This creates and sends that authentication as well as defaults us to
    an authenticated state unless we get an error back indicating otherwise.

    Grapevine 1.0.0
    """
    payload = {'client_id': CLIENT_ID,
               'client_secret': SECRET_KEY,
               'supports': supports,
               'channels': channels,
               'version': version,
               'user_agent': user_agent}

    # If we haven't assigned any channels, lets pull that out of our auth
    # so we aren't trying to auth to an empty string.  This also causes us
    # to receive an error back from Grapevine.
    if not channels:
        payload.pop('channels')

    msg = {'event': 'authenticate',
           'payload': payload}

    status.grapevine['authenticated'] = True

    asyncio.create_task(messages_to_grapevine.put((json.dumps(msg, sort_keys=True, indent=4))))


async def msg_gen_heartbeat() -> None:
    """
    Once registered to Grapevine we will receive regular heartbeats.  The
    docs indicate to respond with the below heartbeat response which
    also provides an update player logged in list to the network.

    Grapevine 1.0.0
    """
    # The below line builds a list of player names logged into Akrios for sending
    # in response to a grapevine heartbeat.
    player_list = [player_.name.capitalize() for player_ in player.playerlist]

    payload = {'players': player_list}
    msg = {'event': 'heartbeat',
           'payload': payload}

    asyncio.create_task(messages_to_grapevine.put((json.dumps(msg, sort_keys=True, indent=4))))


async def msg_gen_chan_subscribe(chan=None) -> None:
    """
    Subscribe to a specific channel, or Gossip by default.

    Grapevine 1.0.0
    """
    ref = str(uuid.uuid4())
    if not chan:
        payload = {'channel': 'gossip'}
    else:
        payload = {'channel': chan}

    if payload['channel'] in subscribed:
        return

    msg = {'event': 'channels/subscribe',
           'ref': ref,
           'payload': payload}

    sent_refs[ref] = msg

    asyncio.create_task(messages_to_grapevine.put((json.dumps(msg, sort_keys=True, indent=4))))


async def msg_gen_chan_unsubscribe(chan=None) -> None:
    """
    Unsubscribe from a specific channel, default to Gossip channel if
    none given.

    Grapevine 1.0.0
    """
    ref = str(uuid.uuid4())
    if not chan:
        payload = {'channel': 'gossip'}
    else:
        payload = {'channel': chan}

    msg = {'event': 'channels/unsubscribe',
           'ref': ref,
           'payload': payload}

    sent_refs[ref] = msg

    asyncio.create_task(messages_to_grapevine.put((json.dumps(msg, sort_keys=True, indent=4))))


async def msg_gen_player_login(player_name) -> None:
    """
    Notify the Grapevine network of a player login.

    Grapevine 1.0.0
    """
    ref = str(uuid.uuid4())
    payload = {'name': player_name.capitalize()}
    msg = {'event': 'players/sign-in',
           'ref': ref,
           'payload': payload}

    sent_refs[ref] = msg

    asyncio.create_task(messages_to_grapevine.put((json.dumps(msg, sort_keys=True, indent=4))))


async def msg_gen_player_logout(player_name) -> None:
    """
    Notify the Grapevine network of a player logout.

    Grapevine 1.0.0
    """
    ref = str(uuid.uuid4())
    payload = {'name': player_name.capitalize()}
    msg = {'event': 'players/sign-out',
           'ref': ref,
           'payload': payload}

    sent_refs[ref] = msg

    asyncio.create_task(messages_to_grapevine.put((json.dumps(msg, sort_keys=True, indent=4))))


async def msg_gen_message_channel_send(caller, channel, message) -> None:
    """
    Sends a channel message to the Grapevine network.  If we're not showing
    as subscribed on our end, we bail out.

    Grapevine 1.0.0
    """
    if channel not in subscribed:
        return

    ref = str(uuid.uuid4())
    payload = {'channel': channel,
               'name': caller.disp_name,
               'message': message[:290]}
    msg = {'event': 'channels/send',
           'ref': ref,
           'payload': payload}

    log.info(f"Grapevine message: {caller.disp_name} on {channel} said '{message}'")

    sent_refs[ref] = msg

    asyncio.create_task(messages_to_grapevine.put((json.dumps(msg, sort_keys=True, indent=4))))


async def msg_gen_game_all_status_query() -> None:
    """
    Request for all games to send full status update.  You will receive in
    return from each game quite a bit of detailed information.  See the
    grapevine.haus Documentation or review the receiver code above.

    Grapevine 2.1.0
    """
    ref = str(uuid.uuid4())

    msg = {'events': 'games/status',
           'ref': ref}

    sent_refs[ref] = msg

    asyncio.create_task(messages_to_grapevine.put((json.dumps(msg, sort_keys=True, indent=4))))


async def msg_gen_game_single_status_query(game) -> None:
    """
    Request for a single game to send full status update.  You will receive in
    return from each game quite a bit of detailed information.  See the
    grapevine.haus Documentation or review the receiver code above.

    Grapevine 2.1.0
    """
    ref = str(uuid.uuid4())

    msg = {'events': 'games/status',
           'ref': ref,
           'payload': {'game': game}}

    sent_refs[ref] = msg

    asyncio.create_task(messages_to_grapevine.put((json.dumps(msg, sort_keys=True, indent=4))))


async def msg_gen_player_status_query() -> None:
    """
    This requests a player list status update from all connected games.

    Grapevine 1.1.0
    """
    ref = str(uuid.uuid4())

    msg = {'event': 'players/status',
           'ref': ref}

    sent_refs[ref] = msg

    asyncio.create_task(messages_to_grapevine.put((json.dumps(msg, sort_keys=True, indent=4))))


async def msg_gen_player_single_status_query(game) -> None:
    """
    Request a player list status update from a single connected game.

    Grapevine 1.1.0
    """
    ref = str(uuid.uuid4())

    msg = {'events': 'players/status',
           'ref': ref,
           'payload': {'game': game}}

    sent_refs[ref] = msg

    asyncio.create_task(messages_to_grapevine.put((json.dumps(msg, sort_keys=True, indent=4))))


async def msg_gen_player_tells(caller_name, game, target, message):
    """
    Send a tell message to a player on the Grapevine network.

    Grapevine 2.0.0
    """
    game = game.capitalize()
    target = target.capitalize()

    ref = str(uuid.uuid4())
    time_now = f'{datetime.datetime.utcnow().replace(microsecond=0).isoformat()}Z'
    payload = {'from_name': caller_name,
               'to_game': game,
               'to_name': target,
               'sent_at': time_now,
               'message': message[:290]}

    msg = {'event': 'tells/send',
           'ref': ref,
           'payload': payload}

    log.info(f"Grapevine tell: {caller_name} to {target}@{game} said '{message}'")

    sent_refs[ref] = msg

    asyncio.create_task(messages_to_grapevine.put((json.dumps(msg, sort_keys=True, indent=4))))


async def msg_gen_achievements_sync() -> None:
    """
    Request the list of achievements for our game.

    Grapevine 2.3.0
    """
    ref = str(uuid.uuid4())

    msg = {'events': 'achievements/sync',
           'ref': ref}

    sent_refs[ref] = msg

    asyncio.create_task(messages_to_grapevine.put((json.dumps(msg, sort_keys=True, indent=4))))


async def msg_gen_achievements_create(title='Generic Title', desc='Generic Description',
                                      points=10, display=False, partial=False, total=None) -> None:
    """
    Create a new achievement.

    The payload should contain all of the attributes of an achievement that you wish to
    set.  I have included all fields possible below for reference.

    Grapevine 2.3.0
    """
    ref = str(uuid.uuid4())

    payload = {'title': title,
               'description': desc,
               'points': points,
               'display': display,
               'partial_progress': partial,
               'total_progress': total}

    msg = {'events': 'achievements/create',
           'ref': ref,
           'payload': payload}

    sent_refs[ref] = msg

    asyncio.create_task(messages_to_grapevine.put((json.dumps(msg, sort_keys=True, indent=4))))


async def msg_gen_achievements_update(key, title='Generic Title', desc='Generic Description',
                                      points=0, display=False, partial=False, total=None) -> None:
    """
    Update an existing achievement

    Per the documentation we utilize the same event type of 'achievements/create' and include
    the unique key in the payload.  You only need to provide the payload fields you wish to
    update.  We have included all fields possible below for reference.  Modify for your needs.

    Grapevine 2.3.0
    """
    ref = str(uuid.uuid4())

    payload = {'key': key,
               'title': title,
               'description': desc,
               'points': points,
               'display': display,
               'partial_progress': partial,
               'total_progress': total}

    msg = {'events': 'achievements/update',
           'ref': ref,
           'payload': payload}

    sent_refs[ref] = msg

    asyncio.create_task(messages_to_grapevine.put((json.dumps(msg, sort_keys=True, indent=4))))


async def msg_gen_achievements_delete(key) -> None:
    """
    Delete an existing achievement.

    Provide the unique key for the achievement, provide as the payload to delete
    the achievement on Grapevine.

    Grapevine 2.3.0
    """
    ref = str(uuid.uuid4())

    payload = {'key': key}

    msg = {'events': 'achievements/delete',
           'ref': ref,
           'payload': payload}

    sent_refs[ref] = msg

    asyncio.create_task(messages_to_grapevine.put((json.dumps(msg, sort_keys=True, indent=4))))
