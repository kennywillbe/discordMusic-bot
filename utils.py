from discord.ext import commands
import discord
import requests
import time
import aiohttp


class utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="sa")
    async def sa(self, ctx):
        await ctx.send("**Vo aleyna aleykum selam!**")

    @commands.command(
        name="delete", help="Deletes a specified number of messages in the channel"
    )
    async def delete(self, ctx, num_messages: int):
        if ctx.author.guild_permissions.manage_messages:
            deleting = discord.Embed(
                description=(f"Deleting {(num_messages)} messages"),
                color=discord.Color.orange(),
            )
            await ctx.send(embed=deleting)
            deleted = await ctx.channel.purge(limit=num_messages + 1)
            msg = discord.Embed(
                description=f"Deleted {len(deleted)-1} messages.",
                color=discord.Color.red(),
            )
            await ctx.send(embed=msg, delete_after=3)
            await deleting.delete()
        else:
            await ctx.send("```You don't have permission to delete messages.```")

    @commands.command(name="avatar")
    async def avatar(self, ctx, *, member: discord.Member = None):
        if member is None:
            member = ctx.author
        embed = discord.Embed(title=f"{member}'s Avatar", color=discord.Color.blue())
        embed.set_image(url=member.avatar)
        await ctx.send(embed=embed)

    @commands.command(name="price")
    async def get_price(self, ctx, arg1):
        if not arg1:
            await ctx.send(f"```Not found```")
            return

        url = "https://api.coingecko.com/api/v3/coins/"

        response = requests.get(url)
        data = response.json()

        if not data:
            await ctx.send("```Data is not found!```")
            return

        coin = next(
            filter(lambda i: i["symbol"] == arg1.lower(), data),
            None,
        )

        if not coin:
            embed = discord.Embed(color=discord.Color.red(), title="Coin is not found!")
            await ctx.send(embed=embed)
            return

        name = coin["name"]
        symbol = coin["symbol"].upper()
        usd_price = coin["market_data"]["current_price"]["usd"]
        embed = discord.Embed(
            color=discord.Color.blue(),
            title=f"{name} ({symbol}) price: ${usd_price}",
        )
        embed.set_thumbnail(url=coin["image"]["thumb"])
        embed.set_footer(text="Developed by @kenny_json")

        change_24h = "{}%".format(
            round(coin["market_data"]["price_change_percentage_24h"], 2)
        )
        embed.add_field(name="Change 24H", value=change_24h)

        price_change = "{} $".format(round(coin["market_data"]["price_change_24h"], 2))
        embed.add_field(name="Price Change 24H", value=price_change)

        high = coin["market_data"]["high_24h"]["usd"]
        low = coin["market_data"]["low_24h"]["usd"]
        high_low = "{}/{} $".format(high, low)
        embed.add_field(name="24H High/Low", value=high_low)

        market_cap = "{:,} $".format(coin["market_data"]["market_cap"]["usd"])
        embed.add_field(name="Market Cap", value=market_cap)

        Volume = "{:,} $".format(coin["market_data"]["total_volume"]["usd"])
        embed.add_field(name="Volume", value=Volume)

        await ctx.send(embed=embed)

    @commands.command(name="inittype")
    async def inittype(self, ctx):
        for i in range(10):
            await ctx.send("a")

    @commands.command(name="ping")
    async def ping_command(self, ctx):
        start = time.perf_counter()
        pong_embed = discord.Embed(title="Pong")
        await ctx.send(embed=pong_embed, delete_after=0.001)
        end = time.perf_counter()
        duration = end - start
        ping_embed = discord.Embed(
            title="pong :ping_pong:",
            description=f":hourglass: Response time: {duration:.2f} seconds",
        )
        await ctx.send(embed=ping_embed)
