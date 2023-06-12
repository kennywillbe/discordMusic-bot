import discord
from discord.ext import commands, tasks

from connection import connection

import asyncio
import time
from youtube_dl import DownloadError


class connections(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.rooms = []
        self.vc = None
        self.inactivity_timer = 1500

    async def create_new_connection(self, ctx):
        conn = connection(ctx)
        room = await conn.connect(ctx)
        if room:
            self.rooms.append(room)
            asyncio.create_task(self.check_inactivity(room, ctx))
            return room

    async def get_room(self, ctx, should_connect=False):
        voice_channel = None
        if ctx.author and ctx.author.voice and ctx.author.voice.channel:
            voice_channel = ctx.author.voice.channel
        else:
            await ctx.send("```Connect to a voice channel!```")
            raise Exception("...Connect to a voice channel")

        room = next(
            filter(lambda room: room.channel.id == voice_channel.id, self.rooms),
            None,
        )

        if room:
            if room.vc and room.vc.is_connected():
                return room
            else:
                self.rooms.remove(room)
                if not should_connect:
                    await ctx.send("```Bot is not connected!```")
                    raise Exception("...Bot is not connected")

        if not room and not should_connect:
            await ctx.send("```Bot is not connected!```")
            raise Exception("...Bot is not connected")

        if should_connect:
            room = await self.create_new_connection(ctx)
        return room

    async def check_inactivity(self, room, ctx):
        while room.vc and room.vc.is_connected():
            if not room.vc.is_playing() and not room.vc.is_paused():
                await asyncio.sleep(self.inactivity_timer)
                if not room.vc.is_playing() and not room.vc.is_paused():
                    dc_msg = discord.Embed(
                        title="Disconnected",
                        description="Disconnecting due to inactivity",
                        color=discord.Color.red(),
                    )
                    await ctx.send(embed=dc_msg)
                    await room.vc.disconnect()
                    self.rooms.remove(room)
                    break
            else:
                await asyncio.sleep(10)

    @commands.command(aliases=["p"])
    async def play(self, ctx, *args):
        query = " ".join(args)
        try:
            if not args:
                return await ctx.send("Please provide a search query.")

            existing_room = await self.get_room(ctx, True)

            song_url, title = existing_room.search_yt(query)
            if type(song_url) == bool:
                await ctx.send(
                    "Incorrect format try another keyword. This could be due to playlist or a livestream format."
                )
            elif song_url is None:
                await ctx.send("No matching song found.")
            else:
                existing_room.music_queue.append([song_url, title])
                await ctx.send(f"**:notes: {title}** added to **Boomerang Q** :notes:")
                if not existing_room.vc.is_playing():
                    await existing_room.play_music(ctx)

        except Exception as e:
            print(e)
            query = query + " lyrics"
            if isinstance(e, AttributeError) and str(e).startswith(
                "'NoneType' object has no attribute 'get'"
            ):
                existing_room = await self.get_room(ctx, True)
                song_url, title = existing_room.search_yt(query)
                existing_room.music_queue.append([song_url, title])
                await ctx.send(f"**:notes: {title}** added to **Boomerang Q** :notes:")
                if not existing_room.vc.is_playing():
                    await existing_room.play_music(ctx)
            elif isinstance(e) and str(e) in (
                "Server returned 403 Forbidden (access denied)"
            ):
                for i in range(3):
                    time.sleep(3)
                    song_url, title = existing_room.search_yt(query)
                    if type(song_url) == bool:
                        await ctx.send(
                            "Incorrect format try another keyword. This could be due to playlist or a livestream format."
                        )
                    elif song_url is None:
                        await ctx.send("No matching song found.")
                    else:
                        existing_room.music_queue.append([song_url, title])
                        await ctx.send(
                            f"**:notes: {title}** added to **Boomerang Q** :notes:"
                        )
                        if not existing_room.vc.is_playing():
                            await existing_room.play_music(ctx)
                        break
            else:
                await ctx.send("Something went wrong. Please try again.")

    @commands.command(name="pause", help="Pauses the current song being played")
    async def pause(self, ctx):
        room = await self.get_room(ctx)
        await room.pause(ctx)

    @commands.command(name="loop", help="Currently playing song is looped")
    async def loop(self, ctx):
        room = await self.get_room(ctx)
        await room.loop(ctx)

    @commands.command(
        name="endloop", help="Turn off the loop for the currently playing song"
    )
    async def endloop(self, ctx):
        room = await self.get_room(ctx)
        await room.endloop(ctx)

    @commands.command(
        name="resume", aliases=["r"], help="Resumes playing with the discord bot"
    )
    async def resume(self, ctx):
        room = await self.get_room(ctx)
        await room.resume(ctx)

    @commands.command(
        name="skip",
        aliases=["s", "next", "n"],
        help="Skips the current song being played",
    )
    async def skip(self, ctx):
        room = await self.get_room(ctx)
        await room.skip(ctx)

    @commands.command(
        name="queue", aliases=["q"], help="Displays the current songs in queue"
    )
    async def queue(self, ctx):
        room = await self.get_room(ctx)
        await room.printQueue(ctx)

    @commands.command(
        name="leave", aliases=["disconnect", "l", "d"], help="Kick the bot from VC"
    )
    async def leave(self, ctx):
        room = await self.get_room(ctx)
        await room.leave(ctx)
        self.rooms.remove(room)

    @commands.command(name="stop")
    async def stop(self, ctx):
        room = await self.get_room(ctx)
        await room.stop(ctx)

    @commands.command(name="repeat")
    async def repeat(self, ctx):
        room = await self.get_room(ctx)
        await room.repeat(ctx)

    @commands.command(name="roff")
    async def roff(self, ctx):
        room = await self.get_room(ctx)
        await room.roff(ctx)

    @commands.command(name="inittest")
    async def inittest(self, ctx):
        room = await self.get_room(ctx, True)

        msg = await ctx.send("```test initializing```")
        url1 = "https://www.youtube.com/watch?v=qsg1MPG1Wsk"
        url2 = "https://www.youtube.com/watch?v=ZYYKHXqGgZg"
        url3 = "https://www.youtube.com/watch?v=uc-939kYSKU"
        url4 = "https://www.youtube.com/watch?v=QWiXfvNPHmw"
        url5 = "https://www.youtube.com/watch?v=icPHcK_cCF4"

        song1 = room.search_yt(url1)
        song2 = room.search_yt(url2)
        song3 = room.search_yt(url3)
        song4 = room.search_yt(url4)
        song5 = room.search_yt(url5)
        room.music_queue.append([song5, room.channel])
        room.music_queue.append([song1, room.channel])
        room.music_queue.append([song2, room.channel])
        room.music_queue.append([song3, room.channel])
        room.music_queue.append([song4, room.channel])

        await msg.delete()
        msg = await ctx.send("```test initialized```")
        await asyncio.sleep(2)
        await msg.delete()
        if not room.vc.is_playing():
            await room.play_music(ctx)
