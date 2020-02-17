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
from typing import Dict, List

# Third Party

# Project
import player
import area
import color
import db
import frontend
import grapevine
import login
from races import init as races_init
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
        log.info(f'Session Instance created: {self.session}')
        log.info(f'Sessions now: {sessions}')
        asyncio.create_task(self.read(), name=self.session)
        asyncio.create_task(self.send(), name=self.session)

    async def fe_login_failed(self):
        asyncio.create_task(frontend.msg_gen_player_login_failed(self.owner.name, self.session))

    async def fe_login_successful(self):
        asyncio.create_task(frontend.msg_gen_player_login(self.owner.name.capitalize(), self.session))

    async def grape_login_successful(self):
        if grapevine.LIVE:
            asyncio.create_task(grapevine.msg_gen_player_login(self.owner.name))

    async def handle_close(self):
        await frontend.msg_gen_player_logout(self.owner.name.capitalize(), self.session)
        self.state['connected'] = False
        self.state['logged in'] = False
        for tasks in asyncio.all_tasks():
            if self.session == tasks.get_name():
                tasks.cancel()

    async def query_db(self, type_, args_=''):
        if type_ == 'help':
            await db.database_select_help.put((sessions, self.session, args_))

    async def login(self, name=None):
        log.debug(f'hitting login method of Session : {self.session}')
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
                msg = color.colorize(msg)
            else:
                msg = color.decolorize(msg)
            await self.out_buf.put(msg)

    async def send_prompt(self):
        if self.state['logged in']:
            if hasattr(self.owner, "editing"):
                await self.out_buf.put(">")
            elif self.promptable:
                if self.owner.oocflags["afk"]:
                    pretext = '{W[{RAFK{W]{x '
                else:
                    pretext = ''
                output = color.colorize(f'\n\r{pretext}{self.owner.prompt}\n\r')
                await self.out_buf.put(output)

    async def send(self):
        while self.state['connected']:
            message = await self.out_buf.get()
            asyncio.create_task(frontend.msg_gen_player_output(message, self.session))

    async def read(self):
        while self.state['connected']:
            message = await self.in_buf.get()
            asyncio.create_task(self.owner.interp(message))


async def shutdown(signal_: signal.Signals, loop_: asyncio.AbstractEventLoop) -> None:
    """
        shutdown coroutine utilized for cleanup on receipt of certain signals.
        Created and added as a handler to the loop in __main__

        https://www.roguelynn.com/talks/
    """
    log.warning(f'Received exit signal {signal_.name}')

    tasks: List[asyncio.Task] = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]

    log.info(f'Cancelling {len(tasks)} outstanding tasks')

    for task in tasks:
        task.cancel()

    await asyncio.gather(*tasks, return_exceptions=True)
    loop_.stop()


def handle_exception_generic(loop_: asyncio.AbstractEventLoop, context: Dict) -> None:
    msg: str = context.get('exception', context['message'])
    log.warning(f'Caught exception: {msg} in loop: {loop_}')
    log.warning(f'Caught in task: {asyncio.current_task().get_name()}')  # type: ignore


async def handle_messages() -> None:
    while status.server['running']:
        message = await frontend.messages_to_game.get()
        session, msg = message
        if session in sessions:
            asyncio.create_task(sessions[session].in_buf.put(msg))


async def cmd_client_connected(options) -> None:
    uuid, address, port = options
    session = Session(uuid, address, port)
    asyncio.create_task(session.login())


async def cmd_client_disconnected(options) -> None:
    uuid, address, port = options
    if uuid in sessions:
        sessions[uuid].state['link dead'] = True


async def cmd_game_load_players(options) -> None:
    for session in options:
        name, address, port = options[session]
        session = Session(session, address, port)
        asyncio.create_task(session.login(name))


async def handle_commands() -> None:
    commands = {'client_connected': cmd_client_connected,
                'client_disconnected': cmd_client_disconnected,
                'game_load_players': cmd_game_load_players}

    while status.server['running']:
        command = await frontend.commands_to_game.get()
        command_type, options = command
        if command_type in commands:
            asyncio.create_task(commands[command_type](options))


async def cmd_grapevine_tells_send(message):
    caller, target, game, error_msg = message
    message = (f'\n\r{{GGrapevine Tell to {{y{target}@{game}{{G '
               f'returned an Error{{x: {{R{error_msg}{{x')
    for eachplayer in player.playerlist:
        if eachplayer.disp_name == caller:
            if eachplayer.oocflags_stored['grapevine'] == 'true':
                eachplayer.write(message)
                return


async def cmd_grapevine_tells_receive(message):
    sender, target, game, sent, message = message
    message = (f'\n\r{{GGrapevine Tell from {{y{sender}@{game}{{x: '
               f'{{G{message}{{x.\n\rReceived at : {sent}.')
    for eachplayer in player.playerlist:
        if eachplayer.disp_name == target.capitalize():
            if eachplayer.oocflags_stored['grapevine'] == 'true':
                eachplayer.write(message)
                return


async def cmd_grapevine_games_connect(message):
    game = message.capitalize()
    message = f'\n\r{{GGrapevine Status Update: {game} connected to network{{x'

    if message != '':
        grape_enabled = [players for players in player.playerlist
                         if players.oocflags_stored['grapevine'] == 'true']
        for eachplayer in grape_enabled:
            eachplayer.write(message)


async def cmd_grapevine_games_disconnect(message):
    game = message.capitalize()
    message = f'\n\r{{GGrapevine Status Update: {game} disconnected from network{{x'
    if message != '':
        grape_enabled = [players for players in player.playerlist
                         if players.oocflags_stored['grapevine'] == 'true']
        for eachplayer in grape_enabled:
            eachplayer.write(message)


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
        for eachplayer in grape_enabled:
            if channel in eachplayer.oocflags['grapevine_channels']:
                eachplayer.write(message)


async def cmd_grapevine_player_login(message):
    msg = f'\n\r{{GGrapevine Status Update: {message}{{x'

    grape_enabled = [players for players in player.playerlist
                     if players.oocflags_stored['grapevine'] == 'true']
    for eachplayer in grape_enabled:
        eachplayer.write(msg)


async def cmd_grapevine_player_logout(message):
    msg = f'\n\r{{GGrapevine Status Update: {message}{{x'

    grape_enabled = [players for players in player.playerlist
                     if players.oocflags_stored['grapevine'] == 'true']
    for eachplayer in grape_enabled:
        eachplayer.write(msg)


async def handle_grapevine_messages() -> None:
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
            commands[event_type](values)


async def main() -> None:
    log.info('Calling main()')
    tasks = [asyncio.create_task(db.connect(), name='db'),
             asyncio.create_task(frontend.connect(), name='frontend'),
             asyncio.create_task(grapevine.connect(), name='grapevine'),
             asyncio.create_task(handle_commands(), name='server-commands'),
             asyncio.create_task(handle_messages(), name='server-messages'),
             asyncio.create_task(handle_grapevine_messages(), name='grapevine'),
             ]

    log.info('Created engine task list')

    completed, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

    log.info('After waiting on engine tasks.')
    log.info(f'Completed task is:\n\n{completed}\n\n')
    log.info(f'All pending tasks are:\n\r{pending}')


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

    races_init()
    asyncio.gather(area.init())

    status.server['running'] = True

    try:
        loop.run_until_complete(main())
    finally:
        player_quit = 'quit force'

        if status.server['softboot']:
            log.info('Softboot has been executed')
            asyncio.create_task(frontend.msg_gen_game_softboot(wait_time=1))
            player_quit = 'quit force no_notify'

        # server.Server.done has been set to True
        for each_player in sessions.values():
            asyncio.gather(each_player.owner.interp(player_quit))
            asyncio.gather(each_player.handle_close())

        for each_task in asyncio.all_tasks():
            each_task.cancel()

        log.info('Akrios shutdown.')
        loop.close()
