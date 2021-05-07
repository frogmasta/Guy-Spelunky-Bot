import math

from discord import Embed
from discord.ext import menus


class Leaderboard(menus.Menu):
    def __init__(self, title: str, header: str, data: list):
        super().__init__()

        # Public variables
        self.title = title
        self.header = header
        self.data = data

        # Hidden variables
        self._embed = None
        self._page = 1
        self._maxPages = math.ceil(len(data) / 10)  # TODO: WARNING - Can be broken if each entry is too long

    def __repr__(self):
        return f"Leaderboard('title'={self.title}, 'header'={self.header})"

    def __len__(self):
        return self._maxPages

    async def send_initial_message(self, ctx, channel):
        icon = ctx.message.author.avatar_url
        leaderboard = self.generate_leaderboard()

        embed = Embed(title=self.title, color=0xD2691E, description=leaderboard)
        embed.set_footer(text=f"Page {self._page}/{self._maxPages}", icon_url=icon)

        self._embed = embed
        return await ctx.send(embed=self._embed)

    @menus.button('⬅️')
    async def on_arrow_left(self, payload):
        await self.edit_leaderboard(-1)

    @menus.button("➡️")
    async def on_arrow_right(self, payload):
        await self.edit_leaderboard(1)

    async def edit_leaderboard(self, increment):
        icon = self._embed.footer.icon_url

        if 1 <= self._page + increment <= self._maxPages:
            self._page += increment
            leaderboard = self.generate_leaderboard()

            embed = Embed(title=self.title, color=0xD2691E, description=leaderboard)
            embed.set_footer(text=f"Page {self._page}/{self._maxPages}", icon_url=icon)

            self._embed = embed
            await self.message.edit(embed=self._embed)

    async def display_entry(self, ctx, search_term):
        found = None
        for entry in self.data:
            if search_term in entry.values():
                found = entry

        if found is None:
            return await ctx.send("Could not find an entry by that name")

        icon = ctx.message.author.avatar_url
        title = f"{list(found.values())[0]} | {self.title}"
        stats = ""
        for key in found.keys():
            stats += f"{key}: **{found[key]}** "

        embed = Embed(title=title, description=stats, color=0xD2691E)
        embed.set_footer(icon_url=icon)

        self._embed = embed
        await ctx.send(embed=self._embed)

    def generate_leaderboard(self):
        if self.header == '':
            leaderboard = ""
        else:
            leaderboard = f"**{self.header}**\n"

        start_idx = (self._page - 1) * 10
        for idx in range(start_idx, start_idx + 10):
            if idx < len(self.data):
                entry_dict = self.data[idx]
                leaderboard += self.add_row(entry_dict, idx + 1)

        return leaderboard

    @staticmethod
    def add_row(entry_dict, place):
        special_places = ['👑', '🥈', '🥉']

        try:
            place_str = special_places[place - 1]
        except IndexError:
            place_str = f'#{place}'

        row = f"{place_str} - "
        for key in entry_dict:
            row += f"{key.capitalize()}: **{entry_dict[key]}** "

        row += "\n\n"
        return row
