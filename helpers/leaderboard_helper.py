from discord import Embed
from pathlib import Path
from helpers.time_helper import old_file
from discord.ext import menus
import editdistance
import math
import re
import requests


class LeaderboardMenu(menus.Menu):
    def __init__(self, date, runs):
        super().__init__()
        self.date = date
        self.runs = runs
        self.current_page = 1
        self.embed = None

    async def send_initial_message(self, ctx, channel):
        total_pages = math.ceil(len(self.runs) / 10)
        icon = ctx.message.author.avatar_url
        leaderboard = self.generate_leaderboard()

        embed = Embed(title=f"{self.date[4:6]}-{self.date[-2:]}-{self.date[:4]}", color=0xD2691E)
        embed.add_field(name="Daily Leaderboard", value=leaderboard, inline=False)
        embed.set_footer(text=f"Page {self.current_page}/{total_pages}", icon_url=icon)

        self.embed = embed
        return await ctx.send(embed=embed)

    @menus.button("⬆️")
    async def on_arrow_up(self, payload):
        self.edit_leaderboard(1)
        await self.message.edit(embed=self.embed)

    @menus.button("⬇️")
    async def on_arrow_down(self, payload):
        self.edit_leaderboard(-1)
        await self.message.edit(embed=self.embed)

    async def find_name(self, ctx, name):
        player_run = None
        for run in self.runs:
            if editdistance.eval(name.lower(), run.name.lower()) < 2:
                player_run = run

        if player_run is None:
            await ctx.send("Could not find a player by that name!")
            return

        icon = ctx.message.author.avatar_url
        title = f"{player_run.name} | {self.date[4:6]}-{self.date[-2:]}-{self.date[:4]} "
        stats = f"Score: **{player_run.score}** Level: **{convert_level(player_run.level)}**"

        embed = Embed(title=title, description=stats, color=0xD2691E)
        embed.set_footer(icon_url=icon)

        await ctx.send(embed=embed)

    def edit_leaderboard(self, increment):
        footer = self.embed.footer
        pages = list(map(int, re.findall(r'\d+', footer.text)))
        self.current_page = pages[0] + increment

        if 0 < self.current_page <= pages[1]:
            leaderboard = self.generate_leaderboard()

            self.embed.clear_fields()
            self.embed.add_field(name="Daily Leaderboard", value=leaderboard, inline=False)
            self.embed.set_footer(text=f'Page {self.current_page}/{pages[1]}', icon_url=footer.icon_url)

    def generate_leaderboard(self):
        leaderboard = ""

        start_idx = (self.current_page - 1) * 10
        for idx in range(start_idx, start_idx + 10):
            if idx < len(self.runs):
                leaderboard += add_run(self.runs[idx], idx + 1)

        return leaderboard


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


def add_run(run, place=None):
    if not place:
        return f"Name: **{run.name}** Score: **{run.score}** Level: **{convert_level(run.level)}** \n\n"

    special_places = ['👑', '🥈', '🥉']
    if 1 <= place <= 3:
        place_str = special_places[place-1]
    else:
        place_str = f'#{place}'

    return f"{place_str} - Name: **{run.name}** Score: **{run.score}** Level: **{convert_level(run.level)}** \n\n"


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
