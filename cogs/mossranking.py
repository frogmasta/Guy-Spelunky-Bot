from bs4 import BeautifulSoup
import requests
from discord.ext import commands
import discord
from src.leaderboard import Leaderboard
from datetime import datetime
import json
import os
from pathlib import Path


def c(t):
    ttime = datetime.strptime(t, '%m/%d/%y')
    return ((datetime.now() - ttime).days)

categories = {'main': "https://mossranking.com/ranking.php?id_ranking=18", 
            'speed': "https://mossranking.com/ranking.php?id_ranking=20", 
            'score': "https://mossranking.com/ranking.php?id_ranking=21"}

class MossRanking(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def mossranking(self, ctx, *args):
        if not args:
            args = 'main'
        else:
            args = ' '.join(args).lower()
        if args not in categories:
            await ctx.send('not a valid category')
            return
    
        download_leaderboard(args)
        
        with open(f'mossranking_data/{args}.json', "r") as read_file:
            data = json.load(read_file)

        menu = Leaderboard(f"MossRanking - {args.capitalize()}", "", data)
        await menu.start(ctx)

def download_leaderboard(category):
    file_path = f'mossranking_data/{category}.json'

    if not Path(file_path).is_file() or old_file(file_path):
        print('downloading file...')
        data = getData(category)
        with open(file_path, 'w') as fout:
            json.dump(data , fout)
    return "Success"

def old_file(file_path):
    last_modified = datetime.utcfromtimestamp(os.path.getmtime(file_path))
    now = datetime.utcnow()
    return True if (now-last_modified).days >= 1 else False

def getData(category):

    page = requests.get(categories[category])
    soup = BeautifulSoup(page.content, 'html.parser')

    table = soup.find('table', class_='table table-striped table-nonfluid')
    tableElements = table.findAll('tr')

    userData = []

    for elem in tableElements:
        try:
            elemData = elem.findAll('td')

            name = elemData[1].find('span').get_text()
            points = elemData[2].get_text()
            charImg = 'https://mossranking.com' + elemData[3].find('img').get('src')
            userRef = 'https://mossranking.com' + elemData[4].find('a').get('href')

            userData.append({'Name': name, 'Points': points, 'Details': f'[Profile]({userRef})'})
        except:
            pass

    return userData

def setup(bot):
    bot.add_cog(MossRanking(bot))
