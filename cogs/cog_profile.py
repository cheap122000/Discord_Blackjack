import discord
from discord.ext import commands
from discord.commands import Option
from discord.ext.commands.context import Context
from discord.commands.context import ApplicationContext
from functions.tools import guild_ids, send_message
from functions import profile, tools, db_game
from typing import Optional, Union, Tuple
from datetime import datetime

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
                    await ctx.send("!op 需要兩個參數")
                    tools.delete_from_processing(ctx)
                    return
                if str(ctx.author.id) != "355354569049505792":
                    await ctx.send("你才不是 CodingMaster 呢 = =")
                    tools.delete_from_processing(ctx)
                    return
                dc_id = m_s[1].replace("<@!", "").replace(">", "").replace("<@", "")
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

    @commands.slash_command(name="profile", description="查看你的籌碼數量", guild_ids=guild_ids)
    async def s_profile(self, ctx: ApplicationContext, user: discord.Member=None):
        user = user or ctx.author
        embed = profile.get_profile(ctx, user)
        await ctx.respond(embed=embed)

    @commands.slash_command(name="daily", description="獲得每日 1000 Nicoin", guild_ids=guild_ids)
    async def s_daily(self, ctx: ApplicationContext):
        embed = profile.get_daily(ctx)
        await ctx.respond(embed=embed)

    @commands.slash_command(name="pool", description="查看伺服器獎金池餘額", guild_ids=guild_ids)
    async def s_pool(self, ctx: ApplicationContext):
        await get_guild_pool(ctx)

    @commands.slash_command(name="leader_board", description="查看 Nicoin 排行榜", guild_ids=guild_ids)
    async def s_lb(self, ctx: ApplicationContext, scope: Option(str, "選擇範圍", choices=["這個伺服器", "全部伺服器"])):
        await rank(ctx, scope)

async def get_guild_pool(ctx: Optional[Union[Context, ApplicationContext]]):
    db = db_game.DB()
    prize = db.query_guild_pool(ctx.guild.id)
    db.close()
    embed = discord.Embed()
    embed.colour = discord.Colour.green()
    if ctx.guild.icon:
        embed.set_author(name=f"{ctx.guild.name} 的獎金池有 {prize} Nicoin", icon_url=ctx.guild.icon.url)
    else:
        embed.set_author(name=f"{ctx.guild.name} 的獎金池有 {prize} Nicoin")
    await send_message(ctx, embed=embed)

async def rank(ctx: Optional[Union[Context, ApplicationContext]], scope: str):
    embed = discord.Embed()
    embed.colour = discord.Colour.gold()

    if scope == "這個伺服器":
        ids = [str(member.id) for member in ctx.guild.members]
        query_str = "','".join(ids)
        rank = await get_rank(ctx, query_str)
        if ctx.guild.icon:
            embed.set_author(name=f"{ctx.guild.name} 排行榜", icon_url=ctx.guild.icon.url)
        else:
            embed.set_author(name=f"{ctx.guild.name} 排行榜")
        
    else:
        rank = await get_rank(ctx)
        embed.set_author(name="全伺服器排行榜")

    for i, r in enumerate(rank):
        if i == 0:
            embed.add_field(name=f":first_place: {r['user_name']}", value=f"{r['balance']} :coin:", inline=False)
        elif i == 1:
            embed.add_field(name=f":second_place: {r['user_name']}", value=f"{r['balance']} :coin:", inline=False)
        elif i == 2:
            embed.add_field(name=f":third_place: {r['user_name']}", value=f"{r['balance']} :coin:", inline=False)
        elif i == 3:
            embed.add_field(name=f":four: {r['user_name']}", value=f"{r['balance']} :coin:", inline=False)
        elif i == 4:
            embed.add_field(name=f":five: {r['user_name']}", value=f"{r['balance']} :coin:", inline=False)
        elif i == 5:
            embed.add_field(name=f":six: {r['user_name']}", value=f"{r['balance']} :coin:", inline=False)
        elif i == 6:
            embed.add_field(name=f":seven: {r['user_name']}", value=f"{r['balance']} :coin:", inline=False)
        elif i == 7:
            embed.add_field(name=f":eight: {r['user_name']}", value=f"{r['balance']} :coin:", inline=False)
        elif i == 8:
            embed.add_field(name=f":nine: {r['user_name']}", value=f"{r['balance']} :coin:", inline=False)
        elif i == 9:
            embed.add_field(name=f":keycap_ten: {r['user_name']}", value=f"{r['balance']} :coin:", inline=False)

    embed.set_footer(text=f"產生於 {datetime.now().strftime('%Y/%m/%d %H:%M:%S')}")
    await send_message(ctx, embed=embed)

async def get_rank(ctx: Optional[Union[Context, ApplicationContext]], query_str: str=None) -> list:
    db = db_game.DB()
    if query_str:
        rows = db.query_data(f"SELECT * FROM [users] WHERE [dc_id] in ('{query_str}') ORDER BY [currency] DESC LIMIT 5")
        users = []
        for row in rows:
            # user = await tools.bot.fetch_user(row[1])
            user = await ctx.guild.fetch_member(row[1])
            temp = {}
            temp["user_name"] = f"{user.display_name}#{user.discriminator}"
            temp["user_avatar"] = user.display_avatar
            temp["balance"] = row[2]
            users.append(temp)
    
    else:
        rows = db.query_data(f"SELECT * FROM [users] ORDER BY [currency] DESC LIMIT 10")
        users = []
        for row in rows:
            user = await tools.bot.fetch_user(row[1])
            temp = {}
            temp["user_name"] = f"{user.name}#{user.discriminator}"
            temp["user_avatar"] = user.display_avatar
            temp["balance"] = row[2]
            users.append(temp)
    db.close()
    return users