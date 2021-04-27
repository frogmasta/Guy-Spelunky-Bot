import editdistance
from discord.ext import menus
from discord import Embed
from helpers.journal_info import ENTRIES

# Emoji constants
dwelling = "<:DwellingHD:834524602704592997>"
anna = '<:anna:834526425016172616>'
pug = '<:pug:834525991829241916>'
jetpack = '<:jetpack:834527323864825868>'
arrow_trap = '<:arrowtrap:834527852955172924>'


class JournalMenu(menus.Menu):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.embed = None
        self.current_page = 1
        self.max_pages = 211

    async def send_initial_message(self, ctx, channel):
        if self.current_page == 1:
            self.render_homepage()
        else:
            entry = page_num_to_entry(self.current_page)
            self.render_entry(entry)

        return await ctx.send(embed=self.embed)

    @menus.button("⬆️")
    async def on_arrow_up(self, payload):
        if not (0 < self.current_page + 1 <= self.max_pages):
            return

        self.current_page += 1
        await self.edit_journal()

    @menus.button("⬇️")
    async def on_arrow_down(self, payload):
        if not 0 < self.current_page - 1 <= self.max_pages:
            return

        self.current_page -= 1
        await self.edit_journal()

    @menus.button(dwelling)
    async def on_dwelling(self, payload):
        self.current_page = 2
        await self.edit_journal()

    @menus.button(anna)
    async def on_anna(self, payload):
        self.current_page = 18
        await self.edit_journal()

    @menus.button(jetpack)
    async def on_jetpack(self, payload):
        self.current_page = 56
        await self.edit_journal()

    @menus.button(pug)
    async def on_pug(self, payload):
        self.current_page = 110
        await self.edit_journal()

    @menus.button(arrow_trap)
    async def on_arrow_trap(self, payload):
        self.current_page = 188
        await self.edit_journal()

    async def edit_journal(self):
        entry = page_num_to_entry(self.current_page)

        if entry is None:
            self.render_homepage()
        else:
            self.render_entry(entry)

        print(self.embed.image.url)
        await self.message.edit(embed=self.embed)

    def render_homepage(self):
        icon = self.ctx.message.author.avatar_url
        description = f'To scroll through individual pages, react with ⬆️ or ⬇️\n' \
                      f'To jump to Places, react with {dwelling}\n' \
                      f'To jump to People, react with {anna}\n' \
                      f'To jump to Items, react with {jetpack}\n' \
                      f'To jump to Bestiary, react with {pug}\n' \
                      f'To jump to Traps, react with {arrow_trap}'

        embed = Embed(title=f"Journal", description=description, color=0xD2691E)
        embed.set_footer(text=f"Page {self.current_page}/{self.max_pages}", icon_url=icon)

        self.embed = embed

    def render_entry(self, entry):
        icon = self.ctx.message.author.avatar_url

        embed = Embed(title=entry.name, description=entry.description, color=0xD2691E)
        embed.set_image(url=f"https://clrpc.com/ecr-images/{entry.name.replace(' ', '_')}.png")
        embed.set_footer(text=f"Page {self.current_page}/{self.max_pages}", icon_url=icon)

        self.embed = embed

    def goto(self, search_term):
        page_num = get_page_from_name(search_term)

        if page_num is not None:
            self.current_page = page_num
            return "Success"

        return "Failure"


def get_page_from_name(search_term):
    idx = 2
    for section in ENTRIES.values():
        for entry in section:
            if editdistance.eval(entry.name.lower(), search_term.lower()) < 2:
                return idx
            idx += 1

    return None


def page_num_to_entry(num):
    if num <= 1:
        return None
    elif num < 18:
        return ENTRIES["places"][num - 2]
    elif num < 56:
        return ENTRIES["people"][num - 18]
    elif num < 110:
        return ENTRIES["items"][num - 56]
    elif num < 188:
        return ENTRIES["bestiary"][num - 110]
    else:
        return ENTRIES["traps"][num - 188]
