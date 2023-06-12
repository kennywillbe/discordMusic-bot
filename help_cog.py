import discord
from discord.ext import commands


class help_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.help_message = discord.Embed(
            title="commands :v:",
            description="""
**!p <keywords>** - finds the song on youtube and play it on your current channel
**!stop** - stops the current song being played and clears the queue
**!q** - displays the current music queue
**!s/!n** - skips the current song being played
**!l/!d** - disconnected the bot from the voice channel
**!pause** - pauses the current song being played or resumes if already paused
**!r** - resumes playing the current song
**!loop** - starts a loop with the current queue
**!endloop** - ends the loop that was started
**!repeat** - (under development)repeats playing the current song, even if in loop
**!roff** - (under development)repeat off command
**!sa** - in reply "Vo aleyna aleykum salam!" turns to muslims XD
**!delete** - after the command, write how many messages you want to be deleted, it will be deleted
**!avatar @member** - Use the @ key after the !avatar command and type the name of the person you want, it will extract the avatar.
**!price** - Leave 1 space after the !price command and write the symbol of the coin you want, the data of that coin will come
**!ping** - Shows bot's response time in seconds relative to you
""",
        )
        self.text_channel_list = []

    # some debug info so that we know the bot has started
    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                self.text_channel_list.append(channel)

        # await self.send_to_all(self.help_message)

    @commands.command(name="help", help="Displays all the available commands")
    async def help(self, ctx):
        await ctx.send(embed=self.help_message)

    async def send_to_all(self, msg):
        for text_channel in self.text_channel_list:
            await text_channel.send(msg)
