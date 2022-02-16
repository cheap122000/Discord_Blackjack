import discord
from discord.ext.commands import Context
import interactions
from .db_game import DB

def get_ctx_icon(ctx:interactions.CommandContext):
    return f"https://cdn.discordapp.com/avatars/{ctx.author.user.id}/{ctx.author.avatar}.webp?size=1024"

def get_profile(message: Context, ctx: interactions.CommandContext=None, dc_id: int=0):
    db = DB()
    balance = db.query_user_balance(dc_id)
    db.close()
    
    if ctx:
        a = interactions.EmbedAuthor(name=f"{ctx.author.nick} has {balance} Nicoins.", icon_url=get_ctx_icon(ctx))
        embed = interactions.Embed(author=a, color=discord.Colour.green().value)

        return embed
        # await ctx.send(embeds=embed)
    else:
        embed = discord.Embed()
        embed.type = "rich"
        embed.set_author(name=f"{message.author.display_name} has {balance} Nicoins.", icon_url=message.author.avatar_url)
        embed.colour = discord.Colour.green()

        return embed
        # await message.channel.send(embed=embed)

async def get_daily(message: Context, ctx: interactions.CommandContext=None, dc_id: int=0):
    db = DB()
    success, balance = db.get_daily(dc_id)
    db.close()
    if ctx:
        if success:
            a = interactions.EmbedAuthor(name=f"{ctx.author.nick} got daily 1000 Nicoins, now has {balance} Nicoins.", icon_url=get_ctx_icon(ctx))
            embed = interactions.Embed(author=a, color=discord.Colour.green().value)
        else:
            a = interactions.EmbedAuthor(name=f"{ctx.author.nick} had obtained daily Nicoins today, now has {balance} Nicoins.", icon_url=get_ctx_icon(ctx))
            embed = interactions.Embed(author=a, color=discord.Colour.red().value)
        await ctx.send(embeds=embed)
    else:
        if success:
            embed = discord.Embed()
            embed.type = "rich"
            embed.colour = discord.Colour.green()
            embed.set_footer(text=f"{message.author.display_name} got daily 1000 Nicoins, now has {balance} Nicoins.", icon_url=message.author.avatar_url)
        else:
            embed = discord.Embed()
            embed.type = "rich"
            embed.colour = discord.Colour.red()
            embed.set_footer(text=f"{message.author.display_name} had obtained daily Nicoins today, now has {balance} Nicoins", icon_url=message.author.avatar_url)
        await message.channel.send(embed=embed)