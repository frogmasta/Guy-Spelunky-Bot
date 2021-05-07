import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load in environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN1')

# Create bot client
bot = commands.Bot(command_prefix='s!')


# Tells when bot is ready
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game('Spelunky 2'))
    print('Ready!')


# Checks for invalid commands
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("That is not a command!")
        return

    if ctx.command.has_error_handler or ctx.cog.has_error_handler:
        return

    raise error


# Load extensions/cogs
for cog in os.listdir('./cogs'):
    if cog.endswith('.py'):
        try:
            bot.load_extension('cogs.' + cog.removesuffix('.py'))
        except Exception as e:
            print("There has been an error loading a cog")
            raise e

# Run bot
bot.run(TOKEN)
