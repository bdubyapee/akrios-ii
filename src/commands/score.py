#! usr/bin/env python3
# Project: Akrios
# Filename: commands/score.py
#
# Capability: player
# 
# Command Description: This command displays the score informational screen to the player.
#
# By: Jubelo

from commands import *

name = "score"
version = 1

requirements = {'capability': ['player'],
                'generic_fail': "See {WHelp score{x for help with this command.",
                'truth_checks':  [],
                'false_checks': []}


@Command(**requirements)
async def score(caller, args, **kwargs):
    await caller.write("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-={BPlayer Information{x=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-")
    await caller.write(f"{{BName{{x: {caller.disp_name} {caller.title}")
    await caller.write(f"{{BGender{{x: {caller.gender.capitalize():10}  {{BRace{{x: {caller.race.name.capitalize():15} {{BDiscipline{{x: {caller.discipline.capitalize():10}")
    await caller.write(f"{{BShort Desc{{x: {caller.short_description}")
    await caller.write(f"{{BCapabilities{{x: {', '.join(caller.capability)}")
    await caller.write(f"{{BPosition{{x: {caller.position.capitalize()}")
    await caller.write(f"{{BAlignment{{x {caller.alignment:15}  {{BAge{{x: {caller.age:<3} {{BWeight{{x: {caller.weight:<4} {{BHeight{{x: {caller.height['feet']:<2}'{caller.height['inches']:<2}")
    await caller.write("")
    await caller.write(f"{{CPlatinum{{x: {caller.money['platinum']:<10} {{YGold{{x: {caller.money['gold']:<10} {{WSilver{{x: {caller.money['silver']:<10} {{yCopper{{x: {caller.money['copper']:<10}")
    await caller.write("")
    await caller.write(f"        {{BHP{{x: {caller.currenthp:>5}/{caller.maxhp:5}     {{BHitroll{{x: {caller.hitroll:<5}")
    await caller.write(f"  {{BMovement{{x: {caller.currentmovement:>5}/{caller.maxmovement:5}     {{BDamroll{{x: {caller.damroll:<5}")
    await caller.write(f"{{BWill Power{{x: {caller.currentwillpower:5}/{caller.maxwillpower:5}       {{BWimpy{{x: {caller.wimpy:<5}")
    await caller.write("")
    await caller.write(f"{{BFamily{{x: {caller.family or 'None':10} {{BClan{{x: {caller.clan or 'None':10} {{BGuild{{x: {caller.guild or 'None':10} {{BCouncil{{x: {caller.council or 'None':10}")
    await caller.write("")
    await caller.write(f"{{BYou are worshipping{{x: {caller.deity or 'None'}")
    await caller.write(f"You have {{W{caller.skillpoints}{{x skill points to spend.")
    await caller.write("")
    await caller.write("{{BAC Slashing{{X: {0:>2}/{1:<2}         {{BStrength{{x: {2:>2}/{3:<2}          {{BAgility{{x: {4:>2}/{5:<2}".format(caller.currentac['slashing'], caller.baceac['slashing'], caller.current_stat['strength'], caller.maximum_stat['strength'], caller.current_stat['agility'], caller.maximum_stat['agility']))
    await caller.write(" {{BAC Bashing{{x: {0:>2}/{1:<2}     {{BIntelligence{{x: {2:>2}/{3:<2}            {{BSpeed{{x: {4:>2}/{5:<2}".format(caller.currentac['bashing'], caller.baceac['bashing'], caller.current_stat['intelligence'], caller.maximum_stat['intelligence'], caller.current_stat['speed'], caller.maximum_stat['speed']))
    await caller.write("{{BAC Piercing{{x: {0:>2}/{1:<2}           {{BWisdom{{x: {2:>2}/{3:<2}     {{BConstitution{{x: {4:>2}/{5:<2}".format(caller.currentac['piercing'], caller.baceac['piercing'], caller.current_stat['wisdom'], caller.maximum_stat['wisdom'], caller.current_stat['constitution'], caller.maximum_stat['constitution']))
    await caller.write(" {{BAC Lashing{{x: {0:>2}/{1:<2}             {{BLuck{{x: {2:>2}/{3:<2}         {{BCharisma{{x: {4:>2}/{5:<2}".format(caller.currentac['lashing'], caller.baceac['lashing'], caller.current_stat['luck'], caller.maximum_stat['luck'], caller.current_stat['charisma'], caller.maximum_stat['charisma']))
    await caller.write("")
