import discord
from discord.ext import commands
from discord.ext.commands.context import Context
from discord.commands.context import ApplicationContext
from discord.commands import Option
from functions.tools import guild_ids, send_message
from functions import tools, db_game
from typing import Optional, Union, Tuple

class Balance(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.slash_command(name="give", description="把 Nicoins 送給你的朋友(?", guild_ids=guild_ids)
    # @commands.slash_command(name="give", description="Give your Nicoins to friends(?.", guild_ids=[557585386612850708])
    async def s_give(self, ctx: ApplicationContext, user: discord.Member, chips: Option(int, "你要給他多少籌碼呢?", min_value=1)):
        success, balance_author, balance_user = give_chips(ctx, user, chips)
        if success:
            embed = discord.Embed()
            embed.colour = discord.Colour.green()
            embed.set_author(name=f"{ctx.author.display_name} 把 {chips} Nicoins 拿給 {user.display_name}", icon_url=ctx.author.display_avatar)
            embed.add_field(name=f"{ctx.author.display_name}#{ctx.author.discriminator}", value=f"現在有 {balance_author} :coin:", inline=False)
            embed.add_field(name=f"{user.display_name}#{user.discriminator}", value=f"現在有 {balance_user} :coin:", inline=False)
            await send_message(ctx, f"<@!{ctx.author.id}> 把 {chips} Nicoins 拿給 <@!{user.id}>", embed=embed)
        else:
            await send_message(ctx, "You don't have enough chips", ephemeral=True)

def give_chips(ctx: Optional[Union[Context, ApplicationContext]], user: discord.Member, chips: int) -> Tuple[bool, int, int]:
    db = db_game.DB()
    balance = db.query_user_balance(ctx.author.id)
    if balance < chips:
        db.close()
        return False, balance, 0
    else:
        balance_author = db.get_balance(ctx.author.id, (chips*-1))
        balance_user = db.get_balance(user.id, chips)
        db.close()
        return True, balance_author, balance_user