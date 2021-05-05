import requests
from pathlib import Path
from discord.ext import commands
from datetime import datetime
from operator import itemgetter
from src.leaderboard import Leaderboard
from src.time_helper import convert_date, old_file
from src.help_descriptions import daily_help, sort_help, search_help
from src.run_parser import get_runs


class DailyLeaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sort_dict = {}

    @commands.command(**daily_help)
    async def daily(self, ctx, date=None):
        date = convert_date(date)
        if date == "Failed":
            await ctx.send("It looks like you entered an invalid date!")
            return
        guild_id = self.get_guild(ctx)

        status = download_leaderboard(date)

        print(f"{date[4:6]}-{date[-2:]}-{date[:4]}")

        if status == "Success":
            with open(f'leaderboard_data/{date}', 'rb') as file:
                runs = get_runs(file)

                runs.sort(key=self.sort_dict[guild_id][1], reverse=self.sort_dict[guild_id][0])
                for run in runs:
                    run["level"] = convert_level(run["level"])

                menu = Leaderboard(f"{date[4:6]}-{date[-2:]}-{date[:4]}", "Daily Leaderboard", runs)
                await menu.start(ctx)
        else:
            await ctx.send("It looks like you entered an invalid date!")

    @commands.command(**sort_help)
    async def sort(self, ctx, sort_method):
        guild_id = self.get_guild(ctx)

        sort_method = sort_method.lower()
        if sort_method == "asc" or sort_method == "ascending":
            self.sort_dict[guild_id][0] = False
        elif sort_method == "desc" or sort_method == "descending":
            self.sort_dict[guild_id][0] = True
        elif sort_method == "level":
            self.sort_dict[guild_id][1] = itemgetter("level", "score")
        elif sort_method == "score":
            self.sort_dict[guild_id][1] = itemgetter("score")
        elif sort_method == "name":
            self.sort_dict[guild_id][1] = itemgetter("name")
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
                leaderboard = Leaderboard(date, "Daily Leaderboard", runs)
                await leaderboard.display_entry(ctx, name)

    def get_guild(self, ctx):
        guild_id = ctx.message.guild.id
        if guild_id not in self.sort_dict:
            self.sort_dict[guild_id] = [True, itemgetter("level", "score")]
        return guild_id


def download_leaderboard(date):
    file_path = f'leaderboard_data/{date}'
    if not Path(file_path).is_file() or old_file(date, file_path):
        url = f'http://cdn.spelunky2.net/static/{date}'
        leaderboard = requests.get(url, allow_redirects=True)

        if leaderboard.status_code == 200:
            with open(f'leaderboard_data/{date}', 'wb') as file:
                file.write(leaderboard.content)
        else:
            return "Failure"
    return "Success"


def convert_level(level):
    if level < 5:
        return "1-" + str(level)
    elif level < 9:
        return "2-" + str((level - 4))
    elif level == 9:
        return "3-1"
    elif level < 14:
        return "4-" + str((level - 9))
    elif level == 14:
        return "5-1"
    elif level < 19:
        return "6-" + str((level - 14))
    else:
        return "7-" + str((level - 18))


def setup(bot):
    bot.add_cog(DailyLeaderboard(bot))
