from discord.ext import commands
from bs4 import BeautifulSoup
from helpers.help_descriptions import info_help, invite_help, wiki_help
import requests


class Information(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.myid = "<@568118705553408040>"

    @commands.command(**info_help)
    async def info(self, ctx):
        await ctx.send(f"Hello! I am a bot that can perform various spelunky related commands. If you have suggestions "
                       f"to add for the bot, send them to {self.myid}.")

    @commands.command(**invite_help)
    async def invite(self, ctx):
        await ctx.send('https://discord.com/api/oauth2/authorize?client_id=830957657988005918&permissions=8&scope=bot')

    @commands.command(**wiki_help)
    async def wiki(self, ctx, *search_query):
        search_query = ' '.join(search_query)
        search_url = f"https://spelunky.fandom.com/wiki/Special:Search?query={search_query}"

        search_page = requests.get(search_url)
        soup = BeautifulSoup(search_page.content, 'html.parser')

        results = soup.find_all("li", class_='unified-search__result')
        for result in results:
            search_result_title = result.find('a', class_='unified-search__result__title')
            title = search_result_title.get('data-title')
            description = result.find('div', class_='unified-search__result__content').text

            correct_game = '2' in title or ('Classic' not in title and 'HD' not in title)
            no_ambiguity = 'Disambiguation' not in description
            if correct_game and no_ambiguity:
                link = search_result_title.get('href')
                await ctx.send(link)
                return

        await ctx.send('Could not find a wiki article that matches your search query!')
        return


def setup(bot):
    bot.add_cog(Information(bot))
