#! usr/bin/env python
# Project: Akrios-II
# Filename: db.py
#
# File Description: The database module.
#
# By: Jubelo

# Standard Library
import asyncio
import logging

# Third Party
import aiopg

# Project
import status

log = logging.getLogger(__name__)

db_select_help = asyncio.Queue()  # (sessions, session, keyword)
db_insert_help = asyncio.Queue()  # (sessions, session, sql)


async def select_help_keywords():
    async with aiopg.connect(database='akrios',
                             user='postgres',
                             password='dbPassword123$',
                             host='127.0.0.1') as conn:
        sql = f"""SELECT keywords, section, topics from helps.help WHERE viewable is True;"""
        log.debug(f'Built sql string:\n\r{sql}\n\r')
        async with conn.cursor() as cur:
            log.debug('db.select_help() cursor acquired')
            await cur.execute(sql)
            ret = await cur.fetchall()
            log.debug(f'db.select_help_keywords: result is {ret}')
        if ret:
            return ret
        else:
            log.warning('Unable to query database for help keywords.')


async def select_help(conn):
    while status.db['connected']:
        sessions, session, keyword = await db_select_help.get()
        sql = f"""SELECT description from helps.help WHERE keywords && ARRAY['{keyword}']::varchar[];"""
        log.debug(f'Built sql string:\n\r{sql}\n\r')
        async with conn.cursor() as cur:
            log.debug('db.select_help() cursor acquired')
            await cur.execute(sql)
            ret = await cur.fetchone()
            log.debug(f'db.select_help: result is {ret}')
        if ret:
            await sessions[session].dispatch(ret[0])
        else:
            await sessions[session].dispatch("""I'm sorry, that help doesn't exist.""")


async def insert_help(conn):
    while status.db['connected']:
        sessions, session, sql = await db_insert_help.get()
        log.info(f'Session({session}) sent {sql} to insert_help')


async def connect() -> None:
    """
    Connect to the database.
    Create tasks related to this connection
    """
    while status.server['running']:
        log.info('Connecting to akrios database...')
        async with aiopg.connect(database='akrios',
                                 user='postgres',
                                 password='dbPassword123$',
                                 host='127.0.0.1') as conn:
            log.info('Database connection successful.')
            status.db['connected'] = True

            tasks = [asyncio.create_task(select_help(conn)),
                     asyncio.create_task(insert_help(conn))]
            completed, pending = await asyncio.wait(tasks, return_when='FIRST_COMPLETED')

            log.debug(f'Database connection closed, completed task is: {completed}\n\r')

        status.db['connected'] = False
        log.warning('Connection to database lost!')
