from unicodedata import name
import discord
from discord.ext import commands
from discord.ext.commands.context import Context
from discord.commands import slash_command, Option
from discord.commands.context import ApplicationContext
from functions.tools import guild_ids
from functions import profile, tools, db_game

class c_profile(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(name="p")
    async def profile(self, ctx: Context):
        embed = profile.get_profile(ctx, ctx.author)
        await ctx.send(embed=embed)

    @commands.command(name="daily")
    async def daily(self, ctx: Context):
        embed = profile.get_daily(ctx)
        await ctx.send(embed=embed)

    @commands.command(name="op")
    async def imop(self, ctx: Context):
        if tools.store_to_processing(ctx):
            channel_id = str(ctx.channel.id)
            try:
                m_s = ctx.message.content.lower().split(" ")
                if len(m_s) != 3:
                    await ctx.send("!op needs 2 parameter.")
                    tools.delete_from_processing(ctx)
                    return
                if str(ctx.author.id) != "355354569049505792":
                    await ctx.send("You are not CodingMaster = =")
                    tools.delete_from_processing(ctx)
                    return
                dc_id = m_s[1].replace("<@!", "").replace(">", "")
                give_amount = int(m_s[2])
            except:
                await ctx.send("Your bet amount must be a positive number")
                tools.delete_from_processing(ctx)
                return

            db = db_game.DB()
            balance = db.get_balance(dc_id, give_amount)
            db.close()
            
            await ctx.send(f"<@!{dc_id}> now have {balance} :coin:")
        else:
            await ctx.reply(ctx, "Error! Please wait for the last command finish.")



class s_profile(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @slash_command(name="profile", description="Show your profile.", guild_ids=guild_ids)
    async def profile(self, ctx: ApplicationContext, user: discord.Member=None):
        user = user or ctx.author
        print(user.id)
        embed = profile.get_profile(ctx, user)
        await ctx.respond(embed=embed)

    @slash_command(name="daily", description="Get your daily Nicoins.", guild_ids=guild_ids)
    async def daily(self, ctx: ApplicationContext):
        embed = profile.get_daily(ctx)
        await ctx.respond(embed=embed)