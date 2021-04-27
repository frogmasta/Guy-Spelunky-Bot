from discord.ext import commands
from datetime import datetime
from helpers.time_helper import convert_date
from helpers.leaderboard_helper import LeaderboardMenu, download_leaderboard
from helpers.help_descriptions import daily_help, sort_help, search_help
from helpers.run_parser import get_runs


class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sort_dict = {}

    @commands.command(**daily_help)
    async def daily(self, ctx, date=None):
        date = convert_date(date)
        if date == "Failed":
            await ctx.send("It looks like you entered an invalid date!")
            return
        guild_id = self.new_guild(ctx)

        status = download_leaderboard(date)

        if status == "Success":
            with open(f'leaderboard_data/{date}', 'rb') as file:
                runs = get_runs(file)
                runs.sort(key=self.sort_dict[guild_id][1], reverse=self.sort_dict[guild_id][0])

                menu = LeaderboardMenu(date, runs)
                await menu.start(ctx)
        else:
            await ctx.send("It looks like you entered an invalid date!")

    @commands.command(**sort_help)
    async def sort(self, ctx, sort_method):
        guild_id = self.new_guild(ctx)

        sort_method = sort_method.lower()
        if sort_method == "asc" or sort_method == "ascending":
            self.sort_dict[guild_id][0] = False
        elif sort_method == "desc" or sort_method == "descending":
            self.sort_dict[guild_id][0] = True
        elif sort_method == "level":
            self.sort_dict[guild_id][1] = lambda run: (run.level, run.score)
        elif sort_method == "score":
            self.sort_dict[guild_id][1] = lambda run: run.score
        elif sort_method == "name":
            self.sort_dict[guild_id][1] = lambda run: run.name
        else:
            await ctx.send(f"That is not a valid sort method.")
            return
        await ctx.send("Sort order changed successfully!")

    @commands.command(**search_help)
    async def search(self, ctx, *args):
        date = convert_date(args[0])
        if date == "Failed":
            date = datetime.utcnow().strftime("%Y%m%d")
            name = ' '.join(args)
        else:
            name = ' '.join(args[1:])

        status = download_leaderboard(date)

        if status == "Success":
            with open(f'leaderboard_data/{date}', 'rb') as file:
                runs = get_runs(file)
                leaderboard = LeaderboardMenu(date, runs)
                await leaderboard.find_name(ctx, name)

    def new_guild(self, ctx):
        guild_id = ctx.message.guild.id
        if guild_id not in self.sort_dict:
            self.sort_dict[guild_id] = [True, lambda run: (run.level, run.score)]
        return guild_id


def setup(bot):
    bot.add_cog(Leaderboard(bot))
