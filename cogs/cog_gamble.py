import discord
from discord.ext import commands
from discord.ext.commands.context import Context
from discord.commands import slash_command, Option
from discord.commands.context import ApplicationContext
from functions.tools import *
import random

class GambleGame(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(name="gamble")
    async def c_gamble(self, ctx: Context):
        try:
            m_s = ctx.message.content.lower().split(" ")
            if len(m_s) != 2:
                await ctx.send("!gamble needs 1 parameter.")
                return
            bet_amount = int(m_s[1])
            if bet_amount < 1:
                await ctx.send("Your bet amount must be at least 1 Nicoins.")
                return
        except:
            await ctx.send("Your bet amount must be a positive number")
            return
        await gamble(ctx, bet_amount)

    @slash_command(name="gamble", description="Gamble with your chips.", guild_ids=guild_ids)
    async def s_gamble(self, ctx: ApplicationContext, chips: Option(int, "How many chips you want to gamble?", min_value=1)):
        await gamble(ctx, chips)

async def gamble(ctx: Optional[Union[Context, ApplicationContext]], bet_amount):
    if store_to_processing(ctx):
        embed = discord.Embed()
        embed.type = "rich"

        db = DB()
        success, balance = db.bet(ctx.author.id, bet_amount)
        if success:
            num = random.randint(1, 100)
            if num <= 60:
                prize = db.add_to_pool(ctx.guild.id, bet_amount)
                embed.colour = discord.Colour.red()
                embed.set_author(name=f"{ctx.author.display_name} rolled {num}, lost {bet_amount} Nicoins. Now have {balance} Nicoins", icon_url=ctx.author.display_avatar)
                if ctx.guild.icon:
                    embed.set_footer(text=f"This server's prize pool has {prize} Nicoins.", icon_url=ctx.guild.icon.url)
                else:
                    embed.set_footer(text=f"This server's prize pool has {prize} Nicoins.")
            elif num <= 97:
                balance = db.get_balance(ctx.author.id, bet_amount*2)
                embed.colour = discord.Colour.green()
                embed.set_author(name=f"{ctx.author.display_name} rolled {num}, won {bet_amount} Nicoins. Now have {balance} Nicoins", icon_url=ctx.author.display_avatar)
            else:
                balance = db.get_balance(ctx.author.id, bet_amount*3)
                embed.colour = discord.Colour.gold()
                embed.set_author(name=f"{ctx.author.display_name} rolled {num}, won {bet_amount*2} Nicoins. Now have {balance} Nicoins", icon_url=ctx.author.display_avatar)
            await reply_message(ctx, embed=embed)
        else:
            await reply_message(ctx, content=f"You don't have enough Nicoins. Your balance: {balance} :coin:")
        delete_from_processing(ctx)
        db.close()
    else:
        await reply_message(ctx, "Error! Please wait for the last command finish.")