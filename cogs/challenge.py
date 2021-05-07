import os
import random
from datetime import datetime
from pathlib import Path

from discord import Embed
from discord.ext import commands

Endings = ['Normal', 'Special', 'Cosmic Ocean']

Route = ['Volcano - Temple', 'Volcano - Tide Pool', 'Jungle - Temple', 'Jungle - Tide Pool']

Items = ['Webgun', 'Wooden Shield', "Metal Shield", "Scepter",
         "Plasma Cannon", "Excalibur", "Teleporter", "Camera",
         "Turkey", "Rock Dog", "Axolotl", "Qilin"]

Levels = []
for i in range(1, 7):
    if i in [1, 2, 4, 6]:
        for j in range(1, 5):
            Levels.append(str(i) + '-' + str(j))
    if i in [3, 5]:
        Levels.append(str(i) + '-1')
    # if i in [7]:
    #     for j in range(1, 100):
    #         Levels.append(str(i) + '-' + str(j))

Challenges = [['go ' + x for x in Route], 'kill all shopkeepers', 'remove your HUD',
              ['bring a ' + item + ' to end of run' for item in Items],
              ['curse yourself on ' + level + ' and cant uncurse' for level in Levels], 'rescue the damsel every level',
              'sacrifice as many bodies as possible',
              'pick up no gold', 'kill everyone', 'kill as little as possible', 'play a low% run']


def createChallenge():
    randomEnding = random.choice(Endings)
    numOfChallenges = random.randint(1, 10)
    if numOfChallenges in [1, 2]:
        numOfChallenges = 0
    elif numOfChallenges in [3, 4, 5, 6, 7, 8]:
        numOfChallenges = 1
    elif numOfChallenges in [9, 10]:
        numOfChallenges = 2
    randomChallenges = []
    ChallengesPool = Challenges

    if randomEnding == "Normal":
        ChallengesPool = [x for x in ChallengesPool if
                          x not in [['curse yourself on ' + level + ' and cant uncurse' for level in Levels],
                                    ['bring a ' + item + ' to end of run' for item in Items]]]

    if randomEnding == "Special":
        ChallengesPool = [x for x in ChallengesPool if
                          x not in [['curse yourself on ' + level + ' and cant uncurse' for level in Levels],
                                    ['bring a ' + item + ' to end of run' for item in Items]]]

    if numOfChallenges > 1:
        ChallengesPool = [x for x in ChallengesPool if
                          x not in ['pick up no gold', 'kill everyone', 'kill as little as possible',
                                    'play a low% run']]

    for i in range(numOfChallenges):
        newChallenge = random.choice(ChallengesPool)

        if newChallenge == 'rescue the damsel every level':
            ChallengesPool = [x for x in ChallengesPool if x not in ['sacrifice as many bodies as possible']]
        if newChallenge == 'sacrifice as many bodies as possible':
            ChallengesPool = [x for x in ChallengesPool if x not in ['rescue the damsel every level']]

        ChallengesPool = [x for x in ChallengesPool if x not in [newChallenge]]

        if isinstance(newChallenge, list):
            newChallenge = random.choice(newChallenge)

        randomChallenges.append(newChallenge)

    listChallenges = ''

    for i in randomChallenges:
        if len(randomChallenges) == 1:
            listChallenges = i
            break
        if len(randomChallenges) == 2:
            listChallenges = randomChallenges[0] + ' and ' + randomChallenges[1]
            break
        if randomChallenges.index(i) < (len(randomChallenges) - 1):
            listChallenges = listChallenges + i + ', '
        else:
            listChallenges = listChallenges + 'and ' + i

    if numOfChallenges == 0:
        challenge = 'Try and go for a ' + random.choice(Endings) + ' win.'
    else:
        challenge = 'Try and go for a ' + random.choice(Endings) + ' win where you ' + listChallenges + '.'

    return challenge


class DailyStruggle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.challenges = {}  # dictionary of dates (key) and challenges (value)

    @commands.command()
    async def dailystruggle(self, ctx):
        download_challenges()

        with open("challenge.txt", "r") as read_file:
            data = read_file.read()

        embed = Embed(description=data, color=0xD2691E,
                      title='The Daily Struggle: ' + datetime.utcnow().strftime('%m-%d-%Y'))
        await ctx.send(embed=embed)


def download_challenges():
    file_path = 'challenge.txt'

    if not Path(file_path).is_file() or old_file(file_path):
        print('downloading file...')
        data = createChallenge()
        with open(file_path, "w") as text_file:
            text_file.write(data)
    return "Success"


def old_file(file_path):
    last_modified = datetime.utcfromtimestamp(os.path.getmtime(file_path))
    now = datetime.utcnow()
    return last_modified.date() != now.date()


def setup(bot):
    bot.add_cog(DailyStruggle(bot))

# run once every day


# print(challenge)
