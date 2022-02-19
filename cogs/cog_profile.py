import discord
from discord.ext import commands
from discord.ext.commands.context import Context
from discord.commands import slash_command
from discord.commands.context import ApplicationContext
from functions.tools import guild_ids
from functions import profile

class c_profile(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(name="p")
    async def profile(self, ctx: Context):
        embed = profile.get_profile(ctx)
        await ctx.send(embed=embed)

    @commands.command(name="daily")
    async def daily(self, ctx: Context):
        embed = profile.get_daily(ctx)
        await ctx.send(embed=embed)



class s_profile(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @slash_command(name="profile", description="Show your profile.", guild_ids=guild_ids)
    async def profile(self, ctx: ApplicationContext):
        embed = profile.get_profile(ctx)
        await ctx.respond(embed=embed)

    @slash_command(name="daily", description="Get your daily Nicoins.", guild_ids=guild_ids)
    async def daily(self, ctx: ApplicationContext):
        embed = profile.get_daily(ctx)
        await ctx.respond(embed=embed)