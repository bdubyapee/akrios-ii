#! usr/bin/env python
# Project: Akrios
# Filename: login.py
# 
# File Description: Login system.
# 
# By: Jubelo

import asyncio
import bcrypt
import logging
import os
import time
import json
import uuid

import area
import helpsys
import livingthing
from math_utils import dice, fuzz
import races
import world
import player


log = logging.getLogger(__name__)


class Login(object):
    def __init__(self, name='', softboot=False):
        super().__init__()
        self.lasthost = ""
        self.lasttime = ""
        self.name = name
        self.newchar = {}
        self.newstats = {}
        self.password = ""
        self.sock = None
        self.softboot = softboot
        self.interp = None

    async def clear(self):
        self.interp = self.get_char_name
        self.newchar = {}
        self.newstats = {}
        self.sock = None

    async def greeting(self):
        await self.sock.dispatch(helpsys.get_help('greet', server=True))
        await self.sock.dispatch('\n\rPlease choose a character name: ', trail=False)
                
    async def get_char_name(self, inp):
        inp = inp.lower()
        if len(inp) < 3 or len(inp) > 15:
            await self.sock.dispatch('Character names must be between 3 and 15 characters long.')
            await self.sock.dispatch('Enter a character name: ', trail=False)
        elif len(inp.split()) > 1:
            await self.sock.dispatch('Character names must only contain one word.')
            await self.sock.dispatch('Enter a character name: ', trail=False)
        elif not inp.isalpha():
            await self.sock.dispatch('Character names may only contain letters.')
            await self.sock.dispatch('Enter a character name: ', trail=False)
        elif inp in ['admanthos', 'aludra', 'caerdik', 'malyki',
                     'myst', 'nephium', 'selucia', 'sirian', 'tharian']:
            await self.sock.dispatch('Character name unacceptable.')
            await self.sock.dispatch('Enter a character name: ', trail=False)
        else:
            self.name = inp
            if os.path.exists(f"{world.playerDir}/{self.name}.json"):
                with open(f"{world.playerDir}/{self.name}.json") as playerfile:
                    maybeplayer = json.load(playerfile)
                self.password = maybeplayer['password']
                self.lasttime = maybeplayer['lasttime']
                self.lasthost = maybeplayer['lasthost']
                await self.sock.dispatch('Please enter your password: ', trail=False)
                self.interp = self.get_char_password
                # self.sock.dont_echo()
            else:
                if world.allownewCharacters:
                    await self.sock.dispatch('Is this a new character? ', trail=False)
                    self.interp = self.confirm_new_char
                else:
                    await self.sock.dispatch("I'm sorry, we are not allowing new characters at this time.\n\r")
                    await self.sock.dispatch("Contact jubelo@akriosmud.funcity.org for an invite!")
                    self.sock.handle_close()
                                
    async def get_char_password(self, inp):
        inp = inp.encode("utf-8")
        if not bcrypt.checkpw(inp, self.password.encode("utf-8")):
            await self.sock.dispatch("\n\rI'm sorry, that isn't the correct password. Good bye.")
            await self.sock.fe_login_failed()
            await self.sock.handle_close()
        else:
            # self.sock.do_echo()
            for person in player.playerlist:
                if person.name == self.name:
                    await self.sock.dispatch("\n\rYour character seems to be logged in already.  Reconnecting you.")
                    del person.sock.owner
                    del person.sock
                    testsock = self.sock
                    await self.clear()
                    person.sock = testsock
                    person.sock.owner = person
                    person.sock.promptable = True
                    person.write = person.sock.dispatch
                    log.info(f"{person.name} reconnecting from link death.")
                    return
            log.info(f"{self.name.capitalize()} logged into main menu.")
            await self.sock.dispatch("")
            await self.sock.dispatch("")
            await self.sock.dispatch(f"Welcome back {self.name.capitalize()}!")
            await self.sock.dispatch(f"You last logged in on {self.lasttime}")
            await self.sock.dispatch(f"From this host: {self.lasthost}")
            await self.sock.dispatch("")
            log.info(f"{self.name.capitalize()} logged into main menu. Last login {self.lasttime} from {self.lasthost}")
            self.lasttime = time.ctime()
            self.lasthost = self.sock.host.strip()
            await self.main_menu()
            self.interp = self.main_menu_get_option
                        
    async def confirm_new_char(self, inp):
        inp = inp.lower()
        if inp == "y" or inp == "yes":
            # self.sock.dont_echo()
            await self.sock.dispatch("Please choose a password for this character: ", trail=False)
            self.interp = self.confirm_new_password
        else:
            await self.sock.dispatch("Calm down.  Take a deep breath.  Now, lets try this again shall we?")
            await self.sock.dispatch("Enter a character name: ", trail=False)
            self.interp = self.get_char_name
                        
    async def confirm_new_password(self, inp):
        await self.sock.dispatch("")
        if len(inp) < 8 or len(inp) > 30:
            await self.sock.dispatch("Passwords must be between 8 and 30 characters long.")
            await self.sock.dispatch("Please choose a password for this character: ", trail=False)
        else:
            self.password = inp
            await self.sock.dispatch("Please reenter your password to confirm: ", trail=False)
            self.interp = self.confirm_new_password_reenter
                        
    async def confirm_new_password_reenter(self, inp):
        if inp != self.password:
            self.password = ''
            await self.sock.dispatch('')
            await self.sock.dispatch('Passwords do not match.')
            await self.sock.dispatch('Please choose a password for this character: ', trail=False)
            self.interp = self.confirm_new_password
        else:
            inp = inp.encode('utf-8')
            self.password = bcrypt.hashpw(inp[:71], bcrypt.gensalt(10)).decode('utf-8')
            # self.sock.do_echo()
            await self.show_races()
            await self.sock.dispatch('Please choose a race: ', trail=False)
            self.interp = self.get_race
                        
    async def main_menu(self):
        await self.sock.dispatch('{BWelcome to Akrios{x\n'
                                 '-=-=-=====-=-=-\n'
                                 '1) Login your character\n'
                                 '2) View the Message of the Day\n'
                                 'L) Logout\n'
                                 'D) Delete this character\n'
                                 '\n'
                                 'Please choose an option: ', trail=False)
                
    async def main_menu_get_option(self, inp):
        inp = inp.lower()
        if inp == '1':
            self.interp = self.character_login
            await self.interp()
        elif inp == '2':
            await self.sock.dispatch(helpsys.get_help('motd', server=True))
            await self.sock.dispatch('')
            await self.main_menu()
        elif inp == 'l':
            await self.sock.dispatch('Thanks for playing.  We hope to see you again soon.')
            log.info(f"{self.sock.host} disconnecting from Akrios.")
            asyncio.create_task(self.sock.handle_close())
        elif inp == 'l no_notify':
            asyncio.create_task(self.sock.handle_close('softboot'))
        elif inp == 'd':
            await self.sock.dispatch('Sorry to see you go.  Come again soon!')
            log.info(f"Character {self.name} deleted by {self.sock.host}")
            os.remove(f"{world.playerDir}/{self.name}.json")
            asyncio.create_task(self.sock.handle_close())
        else:
            await self.main_menu()

    async def character_login(self):
        path = f"{world.playerDir}/{self.name}.json"
        if os.path.exists(path):
            log.info(f'Player path exists: {path}')
            newobject = player.Player(path)
            await newobject.load()
            log.info('loaded newobject player')
            testsock = self.sock
            await self.clear()
            newobject.sock = testsock
            newobject.sock.owner = newobject
            log.info(f'newobj.sock = {newobject.sock}')
            log.info(f'newobj.sock.owner = {newobject.sock.owner}')
            newobject.sock.promptable = True
            newobject.sock.state['logged in'] = True
            log.info(f'newobject.sock.state is : {newobject.sock.state}')
            newobject.write = newobject.sock.dispatch
            if not self.softboot:
                await newobject.write("")
                await newobject.sock.dispatch(helpsys.get_help('motd', server=True))
                await newobject.write("")
            log.info(f"{newobject.name.capitalize()} logging in from {newobject.sock.host}.")
            player.playerlist.append(newobject)
            player.playerlist_by_name[newobject.name] = newobject
            player.playerlist_by_aid[newobject.aid] = newobject
            newobject.logpath = os.path.join(world.logDir, f"{newobject.name}.log")
            if newobject.position == "sleeping":
                await newobject.write("You are sleeping.")
            elif not self.softboot:
                await newobject.interp("look")
            if self.softboot:
                await newobject.write('Something feels different.')
            await newobject.sock.grapevine_login()
            await newobject.sock.fe_login_successful()
            newobject.lasttime = time.ctime()
            newobject.lasthost = newobject.sock.host
        else:
            self.sock.dispatch("There seems to be a problem loading your file!  Notify Jubelo.")
            log.error(f"{path} does not exist!")
            await self.main_menu()
            self.interp = self.main_menu_get_option
                        
    async def show_races(self):
        await self.sock.dispatch('')
        await self.sock.dispatch('\n\rCurrently available races of Akrios')
        await self.sock.dispatch('Please type "{Bhelp <race name>{x" for details')
        await self.sock.dispatch('')

        good_races = races.race_names_by_alignment('good')
        neutral_races = races.race_names_by_alignment('neutral')
        evil_races = races.race_names_by_alignment('evil')

        await self.sock.dispatch(f"{{BGood races{{x: {good_races.title()}")
        await self.sock.dispatch(f"{{BNeutral races{{x: {neutral_races.title()}")
        await self.sock.dispatch(f"{{BEvil races{{x: {evil_races.title()}")
        await self.sock.dispatch('')
                        
    async def get_race(self, inp):
        inp = inp.lower()
        if inp in races.racesdict:
            self.newchar['race'] = races.racebyname(inp)
            await self.sock.dispatch('')
            await self.sock.dispatch("Available genders are: {BFemale Male{x")
            await self.sock.dispatch('Please choose a gender: ', trail=False)
            self.interp = self.get_gender
        elif len(inp.split()) > 1:
            if inp.split()[0] == 'help' and inp.split()[1] in races.racesdict:
                self.sock.query_db('help', inp.split()[1])
                await self.show_races()
                await self.sock.dispatch('Please choose a race: ', trail=False)
        else:
            await self.sock.dispatch('That is not a valid race.')
            await self.show_races()
            await self.sock.dispatch('Please choose a race: ', trail=False)

    async def get_gender(self, inp):
        inp = inp.lower()
        if inp in livingthing.genders:
            self.newchar['gender'] = inp
            await self.show_disciplines()
            await self.sock.dispatch('Please choose a base discipline: ', trail=False)
            self.interp = self.get_discipline
        else:
            await self.sock.dispatch("That isn't a valid gender.")
            await self.sock.dispatch("Available genders are: {BFemale Male{x")
            await self.sock.dispatch("Please choose a gender: ", trail=False)
        
    async def show_disciplines(self):
        await self.sock.dispatch('')
        await self.sock.dispatch('Current base disciplines of Akrios:')
        await self.sock.dispatch('Please type "{Bhelp <discipline>{x" for details.')
        await self.sock.dispatch('')
        disciplines = ', '.join(livingthing.disciplines)
        await self.sock.dispatch(f"{{B{disciplines.title()}{{x")
        await self.sock.dispatch('Mystic Mental Physical')
        await self.sock.dispatch('')
        
    async def get_discipline(self, inp):
        inp = inp.lower()
        if inp in livingthing.disciplines:
            self.newchar['discipline'] = inp
            await self.roll_stats()
            await self.show_stats()
            await self.sock.dispatch('Are these statistics acceptable? ', trail=False)
            self.interp = self.get_roll_stats
        elif len(inp.split()) > 1: 
            if inp.split()[0] == 'help' and inp.split()[1] in ['mystic', 'mental', 'physical']:
                self.sock.dispatch(helpsys.get_help(inp.split()[1]))
                await self.show_disciplines()
                await self.sock.dispatch('Please choose a base discipline: ', trail=False)
        else:
            await self.sock.dispatch('That is not a valid discipline.  Choose a discipline: ', trail=False)
            await self.show_disciplines()
            
    async def roll_stats(self):
        bonus = 0
        if dice(1, 20) == 20:
            bonus += 5
        if dice(1, 100) == 100:
            bonus += 10
          
        # Set base stat to the race default
        self.newstats['strength'] = fuzz(-5, 4, self.newchar['race'].strength)
        self.newstats['intelligence'] = fuzz(-5, 4, self.newchar['race'].intelligence)
        self.newstats['wisdom'] = fuzz(-5, 4, self.newchar['race'].wisdom)
        self.newstats['agility'] = fuzz(-5, 4, self.newchar['race'].agility)
        self.newstats['speed'] = fuzz(-5, 4, self.newchar['race'].speed)
        self.newstats['charisma'] = fuzz(-5, 4, self.newchar['race'].charisma)
        self.newstats['luck'] = fuzz(-5, 4, self.newchar['race'].luck)
        self.newstats['constitution'] = fuzz(-5, 4, self.newchar['race'].constitution)
        self.newstats['strength'] += dice(2, 3, bonus)
        self.newstats['intelligence'] += dice(2, 3, bonus)
        self.newstats['wisdom'] += dice(2, 3, bonus)
        self.newstats['agility'] += dice(2, 3, bonus)
        self.newstats['speed'] += dice(2, 3, bonus)
        self.newstats['charisma'] += dice(2, 3, bonus)
        self.newstats['luck'] += dice(2, 3, bonus)
        self.newstats['constitution'] += dice(2, 3, bonus)
        
    async def show_stats(self):
        await self.sock.dispatch('')
        await self.sock.dispatch('Randomly rolled statistics:')
        for item in self.newstats.keys():
            await self.sock.dispatch(f"{item.capitalize()} {{B{self.newstats[item]}{{x")
        await self.sock.dispatch('')
                        
    async def get_roll_stats(self, inp):
        inp = inp.lower()
        if inp == 'y' or inp == 'yes':
            await self.sock.dispatch(helpsys.get_help('motd', server=True))
            await self.sock.dispatch('')
            newplayer = player.Player()
            newplayer.filename = f"{world.playerDir}/{self.name}.json"
            await newplayer.load()
            testsock = self.sock
            newplayer.name = self.name
            newplayer.password = self.password
            newplayer.lasttime = time.ctime()
            newplayer.lasthost = self.sock.host
            newplayer.race = self.newchar['race']
            newplayer.aid = str(uuid.uuid4())
            newplayer.equipped = {k: None for k in newplayer.race.wearlocations}
            newplayer.gender = self.newchar['gender']
            newplayer.discipline = self.newchar['discipline']
            newplayer.position = 'standing'
            newplayer.maximum_stat = self.newstats
            newplayer.current_stat = self.newstats
            await self.clear()
            newplayer.sock = testsock
            newplayer.sock.owner = newplayer
            newplayer.prompt = '{pAkriosMUD{g:{x '
            newplayer.sock.promptable = True
            newplayer.write = newplayer.sock.dispatch
            player.playerlist.append(newplayer)
            player.playerlist_by_name[newplayer.name] = newplayer
            player.playerlist_by_aid[newplayer.aid] = newplayer
            newplayer.sock.state['logged in'] = True
            newroom = area.room_by_vnum_global(1001)
            log.info(f'login just before move, room is : {newroom}')
            await newplayer.move(newroom)
            newplayer.alias['s'] = 'south'
            newplayer.alias['n'] = 'north'
            newplayer.alias['e'] = 'east'
            newplayer.alias['w'] = 'west'
            newplayer.alias['ne'] = 'northeast'
            newplayer.alias['nw'] = 'northwest'
            newplayer.alias['sw'] = 'southwest'
            newplayer.alias['se'] = 'southeast'
            newplayer.alias['l'] = 'look'
            newplayer.alias['page'] = 'beep'
            newplayer.alias['u'] = 'up'
            newplayer.alias['d'] = 'down'
            await newplayer.interp('look')
            log.info(f"{newplayer.name} @ {newplayer.sock.host} is a new character entering Akrios.")
            await newplayer.sock.grapevine_login()
            await newplayer.sock.fe_login_successful()
            del self
        else:
            await self.roll_stats()
            await self.show_stats()
            await self.sock.dispatch('Are these statistics acceptable? ', trail=False)
