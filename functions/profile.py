import discord
from .db_game import DB
from typing import Optional, Union
from discord.ext.commands.context import Context
from discord.commands.context import ApplicationContext

def get_profile(message: Optional[Union[Context, ApplicationContext]]) -> discord.Embed():
    db = DB()
    balance = db.query_user_balance(message.author.id)
    db.close()

    embed = discord.Embed()
    embed.type = "rich"
    embed.set_author(name=f"{message.author.display_name} has {balance} Nicoins.", icon_url=message.author.avatar)
    embed.colour = discord.Colour.green()

    return embed

def get_daily(message:  Optional[Union[Context, ApplicationContext]]) -> discord.Embed():
    db = DB()
    success, balance = db.get_daily(message.author.id)
    db.close()

    if success:
        embed = discord.Embed()
        embed.type = "rich"
        embed.colour = discord.Colour.green()
        embed.set_footer(text=f"{message.author.display_name} got daily 1000 Nicoins, now has {balance} Nicoins.", icon_url=message.author.avatar)
    else:
        embed = discord.Embed()
        embed.type = "rich"
        embed.colour = discord.Colour.red()
        embed.set_footer(text=f"{message.author.display_name} had obtained daily Nicoins today, now has {balance} Nicoins", icon_url=message.author.avatar)

    return embed