import asyncio
import discord
from discord.ext import commands
import logging

# import all of the cogs
from help_cog import help_cog
from connections import connections
from utils import utils

_log = logging.getLogger("discord")

bot = commands.Bot(
    intents=discord.Intents.all(),
    command_prefix="!",
)
bot.remove_command("help")


async def setup():
    await bot.add_cog(help_cog(bot))
    await bot.add_cog(connections(bot))
    await bot.add_cog(utils(bot))


@bot.event
async def on_ready():
    _log.info("Bot is ready!")


asyncio.run(setup())

token = "discord token"
bot.run(token)
