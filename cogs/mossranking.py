import requests
from bs4 import BeautifulSoup
from discord.ext import commands

from src.leaderboard import Leaderboard

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

        data = get_data(args)

        menu = Leaderboard(f"MossRanking - {args.capitalize()}", "", data)
        await menu.start(ctx)


def get_data(category):
    page = requests.get(categories[category])
    soup = BeautifulSoup(page.content, 'html.parser', from_encoding="iso-8859-1")

    table = soup.find('table', class_='table table-striped table-nonfluid')
    tableElements = table.findAll('tr')

    userData = []

    for elem in tableElements:
        try:
            elemData = elem.findAll('td')

            name = elemData[1].find('span').get_text()
            points = elemData[2].get_text()
            userRef = 'https://mossranking.com' + elemData[4].find('a').get('href')

            userData.append({'Name': name, 'Points': points, 'Details': f'[Profile]({userRef})'})
        except:
            pass

    return userData


def setup(bot):
    bot.add_cog(MossRanking(bot))
