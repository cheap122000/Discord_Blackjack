import discord
from discord.ext import commands
from discord.ext.commands.context import Context
from discord.commands.context import ApplicationContext
from functions.tools import guild_ids, send_message
from functions import profile, tools, db_game
from typing import Optional, Union, Tuple

class Profile(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(name="p")
    async def c_profile(self, ctx: Context):
        embed = profile.get_profile(ctx, ctx.author)
        await ctx.send(embed=embed)

    @commands.command(name="daily")
    async def c_daily(self, ctx: Context):
        embed = profile.get_daily(ctx)
        await ctx.send(embed=embed)

    @commands.command(name="pool")
    async def c_pool(self, ctx: Context):
        await get_guild_pool(ctx)

    @commands.command(name="op")
    async def c_imop(self, ctx: Context):
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
            tools.delete_from_processing(ctx)
        else:
            await ctx.reply(ctx, "Error! Please wait for the last command finish.")

    @commands.slash_command(name="profile", description="Show your profile.", guild_ids=guild_ids)
    async def s_profile(self, ctx: ApplicationContext, user: discord.Member=None):
        user = user or ctx.author
        embed = profile.get_profile(ctx, user)
        await ctx.respond(embed=embed)

    @commands.slash_command(name="daily", description="Get your daily Nicoins.", guild_ids=guild_ids)
    async def s_daily(self, ctx: ApplicationContext):
        embed = profile.get_daily(ctx)
        await ctx.respond(embed=embed)

    @commands.slash_command(name="pool", description="Get the server's pool prize.", guild_ids=guild_ids)
    async def s_pool(self, ctx: ApplicationContext):
        await get_guild_pool(ctx)

async def get_guild_pool(ctx: Optional[Union[Context, ApplicationContext]]):
    db = db_game.DB()
    prize = db.query_guild_pool(ctx.guild.id)
    db.close()
    embed = discord.Embed()
    embed.colour = discord.Colour.green()
    if ctx.guild.icon:
        embed.set_author(name=f"This server's prize pool has {prize} Nicoins.", icon_url=ctx.guild.icon.url)
    else:
        embed.set_author(name=f"This server's prize pool has {prize} Nicoins.")
    await send_message(ctx, embed=embed)