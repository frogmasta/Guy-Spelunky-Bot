import requests
from bs4 import BeautifulSoup
from discord.ext import commands

from src.leaderboard import Leaderboard
from src.help_descriptions import mossranking_help

categories = {'main speed': "https://mossranking.com/ranking.php?id_ranking=20",
              'main score': "https://mossranking.com/ranking.php?id_ranking=21"}


class MossRanking(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(**mossranking_help)
    async def mossranking(self, ctx, *args):
        if not args:
            args = 'main speed'
        else:
            args = ' '.join(args).lower()

        global categories
        categories = await getCategories()

        if args not in categories:
            if args == 'categories':
                await ctx.send(f'Categories to choose from: ' + ", ".join([x.title() for x in categories.keys()]))
            else:
                await ctx.send(f'Not a valid category! Categories to choose from: ' + ", ".join(
                    [x.title() for x in categories.keys()]))
            return

        data = await get_data(args)

        menu = Leaderboard(f"MossRanking - {args.title()}", "", data)
        await menu.start(ctx)


async def getCategories():  # TODO: PLEASE change to only download once
    url = 'https://mossranking.com/categories.php?no_game=3&cid='

    categories = {'main speed': "https://mossranking.com/ranking.php?id_ranking=20",
                  'main score': "https://mossranking.com/ranking.php?id_ranking=21"}

    for i in [str(x) for x in [1, 4, 2, 3, 5]]:
        catUrl = url + i
        page = requests.get(catUrl)
        soup = BeautifulSoup(page.content, 'html.parser', from_encoding="iso-8859-1")

        table = soup.find('table')
        tableElements = table.findAll('tr')

        for elem in tableElements:
            try:
                elemData = elem.findAll('td')
                categories[elemData[0].find('a').get_text().lower().strip('\r\n')] = 'https://mossranking.com/' + \
                                                                                     elemData[0].find('a').get('href')
            except:
                pass
    return categories


async def get_data(category):
    global categories
    page = requests.get(categories[category])
    soup = BeautifulSoup(page.content, 'html.parser', from_encoding="iso-8859-1")

    table = soup.find('table', class_='table table-striped table-nonfluid')
    tableElements = table.findAll('tr')

    userData = []

    for elem in tableElements:
        try:
            elemData = elem.findAll('td')

            if category in ['main speed', 'main score']:
                name = elemData[1].find('span').get_text()
                nameRef = 'https://mossranking.com' + elemData[1].find('a').get('href')
                points = elemData[2].get_text()
                pointsRef = 'https://mossranking.com' + elemData[4].find('a').get('href')
                userData.append({'Name': f'[{name}]({nameRef})', 'Points': f'[{points}]({pointsRef})'})
            else:
                name = elemData[1].find('a').get_text()
                nameRef = 'https://mossranking.com' + elemData[1].find('a').get('href')
                time = elemData[2].get_text()
                timeRef = elemData[7].find('a').get('href')
                userData.append({'Name': f'[{name}]({nameRef})', 'Time': f'[{time}]({timeRef})'})
        except:
            pass

    return userData


def setup(bot):
    bot.add_cog(MossRanking(bot))
