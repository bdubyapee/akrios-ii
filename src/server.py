#! usr/bin/env python
# Project: Akrios-II
# Filename: server.py
# 
# File Description: The main server module.
# 
# By: Jubelo

# Standard Library
import argparse
import asyncio
import logging
import signal
import string

# Third Party

# Project
import player
import area
import color
import frontend
import grapevine
import helpsys
import login
import races
import status
from world import server_log

log = logging.getLogger(__name__)

# This is the dict of connected sessions.
sessions = {}

# Assistant variables for removing certain characters from our input.
valid_chars = string.printable.replace(string.whitespace[1:], "")


class Session(object):
    def __init__(self, uuid, address, port):
        self.owner = None
        self.host = address
        self.port = port
        self.session = uuid
        self.ansi = True
        self.promptable = False
        self.in_buf = asyncio.Queue()
        self.out_buf = asyncio.Queue()
        self.state = {'connected': True,
                      'link dead': False,
                      'logged in': False}

        sessions[self.session] = self
        asyncio.create_task(self.read(), name=self.session)
        asyncio.create_task(self.send(), name=self.session)

    async def fe_login_failed(self):
        """
        Let the front end know that this session failed to login (authenticate).
        """
        asyncio.create_task(frontend.msg_gen_player_login_failed(self.owner.name, self.session))

    async def fe_login_successful(self):
        """
        Let the front end know that this session authenticated successfully.
        """
        asyncio.create_task(frontend.msg_gen_player_login(self.owner.name.capitalize(), self.session))

    async def fe_logout_successful(self):
        """
        Let the front end know that this session logged out of the game engine.
        """
        asyncio.create_task(frontend.msg_gen_player_logout(self.owner.name.capitalize(), self.session))

    async def grapevine_login(self):
        """
        Notify the Grapevine system that this player logged into Akrios.
        """
        asyncio.create_task(grapevine.msg_gen_player_login(self.owner.name))

    async def grapevine_logout(self):
        """
        Notify the Grapevine system that this player logged out of Akrios.
        """
        asyncio.create_task(grapevine.msg_gen_player_logout(self.owner.name))

    async def handle_close(self, message=""):
        """
        This player session is ending, for whatever reason, so we need to do some cleanup.
        """
        log.debug(f'performing handle_close, message is: {message}')
        if message != 'softboot':
            # This is a normal disconnect (quitting, idle timeout, etc)
            # Notify the front end to close the session and notify Grapevine of the player logout.
            log.debug(f'handle_close: logging {self.owner.name.capitalize()} out of Grapevine and Front end.')
            await frontend.msg_gen_player_logout(self.owner.name.capitalize(), self.session)
            await grapevine.msg_gen_player_logout(self.owner.name)

        self.state['connected'] = False
        self.state['logged in'] = False

        # Close any remaining tasks in the loop associated with this session.
        for tasks in asyncio.all_tasks():
            if self.session == tasks.get_name():
                tasks.cancel()

    async def login(self, name=None):
        """
        A player has connected, begin the login process.
        """
        # If we are passed a name a softboot has happened.  Set the connection to a login session that will
        # automatically log the player in.
        #     else: Set the session to a new login.
        if name:
            new_conn = login.Login(name, softboot=True)
        else:
            new_conn = login.Login()
        new_conn.sock = self
        new_conn.sock.owner = new_conn
        if not name:
            await new_conn.greeting()
            log.info(f'Accepting connection from: {new_conn.sock.host}')
            new_conn.interp = new_conn.get_char_name
            inp = await self.in_buf.get()
            await new_conn.interp(inp)
        else:
            new_conn.interp = new_conn.character_login
            await new_conn.interp()

    async def dispatch(self, msg, trail=True):
        if self.state['connected']:
            if trail:
                msg = f'{msg}\n\r'
            if self.ansi:
                msg = color.colorize(f'{msg}{{x')
            else:
                msg = color.decolorize(msg)
            await self.out_buf.put((msg, "false"))

    async def send_prompt(self):
        if self.state['logged in']:
            if hasattr(self.owner, "editing"):
                await self.out_buf.put(">")
            elif self.promptable:
                if self.owner.oocflags["afk"]:
                    pretext = '{W[{RAFK{W]{x '
                else:
                    pretext = ''
                output = color.colorize(f'\n\r{pretext}{self.owner.prompt}{{x\n\r')
                await self.out_buf.put((output, "true"))

    async def send(self):
        """
        When we have output to send to the player it will be placed in the out_buf, await for that
        data and as it arrives send the data to the front end for transport to the client.
        """
        while self.state['connected']:
            message, is_prompt = await self.out_buf.get()
            asyncio.create_task(frontend.msg_gen_player_output(message, self.session, is_prompt))

    async def read(self):
        """
        As the connected player enters input, the front end transports that to this engine via websockets.
        When we receive that input it is placed into the session in_buf.  Await input from the player
        and interpret the input.
        """
        while self.state['connected']:
            message = await self.in_buf.get()
            asyncio.create_task(self.owner.interp(message))


async def shutdown(signal_: signal.Signals, loop_: asyncio.AbstractEventLoop):
    """
        shutdown coroutine utilized for cleanup on receipt of certain signals.
        Created and added as a handler to the loop in __main__

        https://www.roguelynn.com/talks/
    """
    log.warning(f'Received exit signal {signal_.name}')

    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]

    log.info(f'Cancelling {len(tasks)} outstanding tasks')

    for task in tasks:
        task.cancel()

    await asyncio.gather(*tasks, return_exceptions=True)
    loop_.stop()


async def shutdown_or_softboot():
    """
    To facilitate shutdown or softboot of the game engine, we have a Queue (in the status module for now)
    which exists to wait for a shutdown/softboot command to occur.  We await something to show up in that
    queue then we proceed to perform appropriate shutdown/softboot actions.
    """
    log.debug('Initial launch of shutdown_or_softboot Task')

    log.debug('Inside while loop of server running, awaiting message from queue')
    message = await status.server_shutdown.get()
    log.debug(f'RECEIVED server_shutdown queue message of : {message}')
    player_quit = 'quit force'

    if message == 'softboot':
        log.info('Softboot has been executed')
        await frontend.msg_gen_game_softboot(wait_time=0.5)
        player_quit = 'quit force no_notify'

    for each_player in sessions.values():
        log.debug('Looping over all players and force quitting')
        await each_player.owner.interp(player_quit)

    log.debug('Sleeping the shutdown_or_softboot Task')
    status.server['running'] = False


def handle_exception_generic(loop_, context):
    """
    A somewhat generic exception handler.  This will be attached to the event loop as the exception handler.
    For now we just log the exception information.
    """
    msg = context.get('exception', context['message'])
    log.warning(f'Caught exception: {msg} in loop: {loop_}')
    log.warning(f'Caught in task: {asyncio.current_task().get_name()}')


async def handle_fe_messages():
    """
    As the front end receives player input, it sends that over to this game engine (handled elsewhere in this
    module). We await any input we receive and put it into the in_buf queue for that particular player session.
    """
    while status.server['running']:
        message = await frontend.messages_to_game.get()
        session, msg = message
        if session in sessions:
            asyncio.create_task(sessions[session].in_buf.put(msg))


async def cmd_fe_client_connected(options):
    """
    We have received a client connected notification from the front end.  Create a session and begin a login
    session.
    """
    uuid, address, port = options
    session = Session(uuid, address, port)
    asyncio.create_task(session.login())


async def cmd_fe_client_disconnected(options):
    """
    We have received a client disconnected notification from the front end.  Since the player did not technically
    quit the game, we place them in a link-dead state.
    """
    uuid, address, port = options
    if uuid in sessions:
        sessions[uuid].state['link dead'] = True


async def cmd_fe_game_load_players(options):
    """
    We have received a game_load_players notification from the front end.  When this game engine starts and connects
    to the Front End, if there are existing sessions already connected to the front end we assume we have either
    performed a softboot, or we crashed and were restarted.   This list from the front end tells us which players
    are connected and their session so that we can auto-log them in.
    """
    for session in options:
        name, address, port = options[session]
        session = Session(session, address, port)
        asyncio.create_task(session.login(name))


async def handle_fe_commands():
    """
    We have received a JSON package from the front end.  Determine the command type parameter and create
    a task, via the appropriate coroutine, to process the payload.
    """
    commands = {'client_connected': cmd_fe_client_connected,
                'client_disconnected': cmd_fe_client_disconnected,
                'game_load_players': cmd_fe_game_load_players}

    while status.server['running']:
        command = await frontend.commands_to_game.get()
        command_type, options = command
        if command_type in commands:
            asyncio.create_task(commands[command_type](options))


async def cmd_grapevine_tells_send(message):
    caller, target, game, error_msg = message
    message = (f'\n\r{{GGrapevine Tell to {{y{target}@{game}{{G '
               f'returned an Error{{x: {{R{error_msg}{{x')
    for each in player.playerlist:
        if each.disp_name == caller and each.oocflags_stored['grapevine'] == 'true':
            await each.write(message)
            return


async def cmd_grapevine_tells_receive(message):
    sender, target, game, sent, message = message
    message = f'\n\r{{GGrapevine Tell from {{y{sender}@{game}{{x: {{G{message}{{x.\n\rReceived at : {sent}.'
    for each in player.playerlist:
        if each.disp_name == target.capitalize() and each.oocflags_stored['grapevine'] == 'true':
            await each.write(message)
            return


async def cmd_grapevine_games_connect(message):
    game = message.capitalize()
    message = f'\n\r{{GGrapevine Status Update: {game} connected to network{{x'

    if message != '':
        grape_enabled = [players for players in player.playerlist
                         if players.oocflags_stored['grapevine'] == 'true']
        for each in grape_enabled:
            await each.write(message)


async def cmd_grapevine_games_disconnect(message):
    game = message.capitalize()
    message = f'\n\r{{GGrapevine Status Update: {game} disconnected from network{{x'
    if message != '':
        grape_enabled = [players for players in player.playerlist
                         if players.oocflags_stored['grapevine'] == 'true']
        for each in grape_enabled:
            await each.write(message)


async def cmd_grapevine_channels_broadcast(message):
    name, game, message, channel = message
    if name is None or game is None:
        log.info('Received channels/broadcast with None type')
        return
    message = (f'\n\r{{GGrapevine {{B{channel}{{x Chat{{x:{{y{name.capitalize()}'
               f'@{game.capitalize()}{{x:{{G{message}{{x')

    if message != '':
        grape_enabled = [players for players in player.playerlist
                         if players.oocflags_stored['grapevine'] == 'true']
        for each in grape_enabled:
            if channel in each.oocflags['grapevine_channels']:
                await each.write(message)


async def cmd_grapevine_player_login(message):
    msg = f'\n\r{{GGrapevine Status Update: {message}{{x'

    grape_enabled = [players for players in player.playerlist
                     if players.oocflags_stored['grapevine'] == 'true']
    for each in grape_enabled:
        await each.write(msg)


async def cmd_grapevine_player_logout(message):
    msg = f'\n\r{{GGrapevine Status Update: {message}{{x'

    grape_enabled = [players for players in player.playerlist
                     if players.oocflags_stored['grapevine'] == 'true']
    for each in grape_enabled:
        await each.write(msg)


async def handle_grapevine_messages():
    commands = {'tells/send': cmd_grapevine_tells_send,
                'tells/receive': cmd_grapevine_tells_receive,
                'games/connect': cmd_grapevine_games_connect,
                'games/disconnect': cmd_grapevine_games_disconnect,
                'channels/broadcast': cmd_grapevine_channels_broadcast,
                'player/login': cmd_grapevine_player_login,
                'player/logout': cmd_grapevine_player_logout}

    while status.grapevine['connected']:
        message = await grapevine.messages_to_game.get()

        log.info(f'server.handle_grapevine_message message is: {message}')

        event_type, values = message
        if event_type in commands:
            await commands[event_type](values)


async def main():
    log.info('Calling main()')
    tasks = [asyncio.create_task(frontend.connect(), name='frontend'),
             asyncio.create_task(grapevine.connect(), name='grapevine'),
             asyncio.create_task(handle_fe_commands(), name='server-commands'),
             asyncio.create_task(handle_fe_messages(), name='server-messages'),
             asyncio.create_task(handle_grapevine_messages(), name='grapevine'),
             asyncio.create_task(shutdown_or_softboot(), name='shutdown-or-softboot')
             ]

    log.info('Created engine task list')

    completed, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

    log.info('After waiting on engine tasks.')
    log.info(f'Completed task is:\n\n{completed}\n\n')

    for task in pending:
        task.cancel()


if __name__ == '__main__':
    log.info('Starting Akrios.')

    parser = argparse.ArgumentParser(
        description='Change the option prefix characters',
        prefix_chars='-+/',
    )

    parser.add_argument('-d', action='store_true',
                        default=None,
                        help='Set log level to debug',
                        )

    args = parser.parse_args()

    logging.basicConfig(filename=server_log, filemode='w',
                        format='%(asctime)s: %(name)s - %(levelname)s - %(message)s',
                        level=logging.DEBUG if args.d else logging.INFO)
    log: logging.Logger = logging.getLogger(__name__)

    loop = asyncio.get_event_loop()

    for sig in (signal.SIGHUP, signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown(sig, loop)))

    loop.set_exception_handler(handle_exception_generic)

    helpsys.init()
    races.init()
    asyncio.gather(area.init())

    try:
        loop.run_until_complete(main())
    finally:
        log.info('Akrios shutdown.')
        loop.close()
