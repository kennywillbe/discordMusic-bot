import asyncio
import discord
from discord.ext import commands

from youtube_dl import YoutubeDL
from asyncio import run


class connection(commands.Cog):
    def __init__(self, ctx):
        self.vc = None
        self.channel = None
        self.bot = None

        self.music_queue = []
        self.current_idx = 0
        self.is_loop = False
        self.is_repeat = False
        self.YDL_OPTIONS = {
            "format": "bestaudio",
            "default_search": "ytsearch",
            "quiet": True,
            "no_warnings": True,
            "noplaylist": False,
            "age_limit": 99,
            "ignoreerrors": True,
        }

        self.FFMPEG_OPTIONS = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn",
        }

    async def connect(self, ctx):
        channel = ctx.author.voice.channel
        connected_channel = await channel.connect()
        if not connected_channel:
            await ctx.send("Could not connect to the voice channel")
            return

        self.channel = channel
        self.vc = connected_channel
        self.bot = ctx.bot

        # ctx.bot.loop.create_task(self.player_loop(ctx))

        return self

    # searching the item on youtube
    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info(item, download=False)
            except Exception:
                print("Error occurred while trying to fetch the video")
                return False

        if "entries" in info:  # If the result is a playlist
            for entry in info["entries"]:
                if entry.get("is_live", False) is not True:  # Skip live streams
                    return entry["formats"][0]["url"], entry["title"]
            return False  # Return False if no suitable video is found
        elif "formats" in info:  # If the result is a single video
            return info["formats"][0]["url"], info["title"]
        else:
            return False

    async def player_loop(self, ctx):
        await self.bot.wait_until_ready()

        while not ctx.bot.is_closed():
            if not self.vc:
                continue
            if not self.music_queue:
                continue

            elif self.vc.is_playing():
                continue

            if self.is_repeat and self.vc.is_paused():
                self.vc.resume()
            if not self.vc.is_playing():
                m_url = self.music_queue[self.current_idx][0]["source"]
                self.vc.play(
                    discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS),
                )

            if self.is_loop:
                if not self.is_repeat:
                    self.current_idx = (self.current_idx + 1) % len(self.music_queue)
                else:
                    self.music_queue.pop(self.current_idx)

            await asyncio.sleep(1)

    def play_next(self, ctx):
        if self.vc.is_playing():
            return

        if self.is_repeat and self.vc.is_paused():
            # await self.vc.resume()
            return

        if self.is_loop:
            if not self.is_repeat:
                self.current_idx = (self.current_idx + 1) % len(self.music_queue)
        elif self.music_queue:
            self.music_queue.pop(self.current_idx)

        if self.music_queue:
            m_url = self.music_queue[self.current_idx][0]
            self.vc.play(
                discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS),
                after=lambda e: self.play_next(ctx),
            )
        # else:
        #     asyncio.create_task(
        #         ctx.send("```playlist is finished, search for songs with !p!```")
        #     )

    async def play_music(self, ctx):
        try:
            if self.music_queue:
                m_url = self.music_queue[self.current_idx][0]
                self.vc.play(
                    discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS),
                    after=lambda e: self.play_next(ctx),
                )
            else:
                await ctx.send("he he")
        except Exception as e:
            print(e)
            await ctx.send("Something went wrong while playing the song. Try again!")

    async def pause(self, ctx):
        if self.vc.is_playing():
            self.vc.pause()
            await ctx.send("```The music has been paused!```")
        elif len(self.music_queue) <= 0:
            await ctx.send("```There is no music playing to pause!```")

    async def loop(self, ctx):
        if self.is_loop:
            await ctx.send("```Loop is already on!```")
        else:
            self.is_loop = True
            await ctx.send("```Loop on!```")

    async def endloop(self, ctx):
        if self.is_loop:
            self.is_loop = False
            self.music_queue = self.music_queue[self.current_idx :]
            self.current_idx = 0
            await ctx.send("```Loop off!```")
        else:
            await ctx.send("```Loop is already off!```")

    async def resume(self, ctx):
        if self.vc.is_paused():
            self.vc.resume()
            await ctx.send("```The music continues!```")
        else:
            await ctx.send("```Can't resume because there is no music in q```")

    async def skip(self, ctx):
        if self.vc.is_playing():
            self.vc.stop()

        if not self.music_queue:
            await ctx.send("```No tracks in queue!```")
            return

        if self.is_repeat:
            self.is_repeat = False

        await ctx.send("```Song skipped!```")
        self.play_next(ctx)

    async def printQueue(self, ctx):
        if self.music_queue:
            songs_in_queue = "\n".join(
                f"{i+1}) {self.music_queue[i][1]} {'< Now playing' if i == self.current_idx else ''}"
                for i in range(min(len(self.music_queue), 50))
            )
            embed = discord.Embed(title="Music Queue", description=songs_in_queue)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Music Queue", description="**No music in queue**"
            )
            await ctx.send(embed=embed)

    async def leave(self, ctx):
        self.vc.stop()
        self.is_loop = False
        await self.vc.disconnect()
        await ctx.send("```The music bot has left the voice channel!```")

    async def stop(self, ctx):
        self.vc.stop()
        self.is_loop = False
        self.is_repeat = False

        if not self.music_queue:
            await ctx.send("```sira bos```")
            return

        self.music_queue = []
        self.current_idx = 0

        await ctx.send("```The player has stopped and the queue has been cleared```")

    async def repeat(self, ctx):
        if not self.is_repeat:
            self.is_repeat = True
            embed = discord.Embed(title="Repeat on!")
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="Repeat is already on!")
            await ctx.send(embed=embed)

    async def roff(self, ctx):
        if self.is_repeat:
            self.is_repeat = False
            embed = discord.Embed(title="Repeat off")
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="Repeat is already off!")
            await ctx.send(embed=embed)
