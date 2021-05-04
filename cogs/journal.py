from discord.ext import commands
from src.journal_menu import JournalMenu
from src.help_descriptions import journal_help


class Journal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(**journal_help)
    async def journal(self, ctx, *entry_name):
        journal = JournalMenu(self.bot)

        if entry_name:
            search_term = ' '.join(entry_name).lower()
            status = journal.goto(search_term)
            if status == "Failure":
                await ctx.send("Could not find a journal entry by that name!")
                return

        await journal.start(ctx)


def setup(bot):
    bot.add_cog(Journal(bot))
