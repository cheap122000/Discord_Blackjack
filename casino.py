from unicodedata import name
import discord
from discord.ext.commands import Bot, Context
import interactions
import json
import random
import time
import asyncio
import os, shutil
from games.game_config import *
# from functions import help_center
import longman
# import functions.profile as profile
from functions import profile, tools, help_center
from games import blackjack

with open("./token_dev.txt", "r", encoding="utf8") as f:
    token = f.read()

bot = interactions.Client(token)
# client = discord.ext.commands.Bot(command_prefix="bj!")
client = Bot(command_prefix="bj!")
client.remove_command("help")
hpc = help_center.helpCenter()

if not os.path.exists("./db_bj.db3"):
    shutil.copy("./db_bj2.db3", "./db_bj.db3")
    
guild_ids = tools.get_guild_ids()

processing_channel = {}
processing_user = {}

# game_records = {}

def store_to_processing(message, ctx:interactions.CommandContext=None):
    if is_in_processing(message, ctx):
        return False
    else:
        if ctx:
            processing_channel[str(ctx.channel_id)] = int(time.time())
            processing_user[str(ctx.author.user.id)] = int(time.time())
            return True
        else:
            processing_channel[str(message.channel.id)] = int(time.time())
            processing_user[str(message.author.id)] = int(time.time())
            return True

def delete_from_processing(message, ctx:interactions.CommandContext=None):
    if ctx:
        processing_channel.pop(str(ctx.channel_id))
        processing_user.pop(str(ctx.author.user.id))
    else:
        processing_channel.pop(str(message.channel.id))
        processing_user.pop(str(message.author.id))

def is_in_processing(message:Context, ctx:interactions.CommandContext=None):
    if ctx:
        p_time = processing_channel.get(str(ctx.channel_id))
        now_time = int(time.time())
        if p_time:
            if now_time - p_time < 30:
                return True
        
        p_time = processing_user.get(str(ctx.author.user.id))
        if p_time:
            if now_time - p_time < 30:
                return True

        return False
    else:
        p_time = processing_channel.get(str(message.channel.id))
        now_time = int(time.time())
        if p_time:
            if now_time - p_time < 30:
                return True
        
        p_time = processing_user.get(str(message.author.id))
        if p_time:
            if now_time - p_time < 30:
                return True

        return False

def get_ctx_icon(ctx:interactions.CommandContext):
    return f"https://cdn.discordapp.com/avatars/{ctx.author.user.id}/{ctx.author.avatar}.webp?size=1024"

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@client.event
async def on_guild_join(guild):
    tools.add_guild_to_db(guild.id)

@bot.event
async def on_ready():
    print("Interactions ready")

# help
@client.command(name="help")
async def c_help(message: Context):
    await message.channel.send(embed=hpc.set_help_center(message))

@bot.command(name="help", description="Help Center", scope=guild_ids)
async def c__help(ctx: interactions.CommandContext):
    print('HELP')
    await ctx.send(embeds=hpc.set_help_center("", ctx))

# profile
@client.command(name="p")
async def c_profile(message: Context):
    if store_to_processing(message):
        embed = profile.get_profile(message, ctx=None, dc_id=message.author.id)
        await message.channel.send(embed=embed)
        delete_from_processing(message)
    else:
        await message.reply("Error! Please wait for the last command finish.")

@bot.command(name="profile", description="Show your profile", scope=guild_ids)
async def c__profile(ctx: interactions.CommandContext):
    if store_to_processing("", ctx):
        embed = profile.get_profile("", ctx=ctx, dc_id=ctx.author.user.id)
        await ctx.send(embeds=embed)
        delete_from_processing("", ctx)
    else:
        await ctx.send("Error! Please wait for the last command finish.")

#daily
@client.command(name="daily")
async def c_daily(message: Context):
    if store_to_processing(message):
        await profile.get_daily(message, ctx=None, dc_id=message.author.id)
        delete_from_processing(message)
    else:
        await message.reply("Error! Please wait for the last command finish.")

@bot.command(name="daily", description="Obtain daily 1000 Nicoins", scope=guild_ids)
async def c__daily(ctx: interactions.CommandContext):
    if store_to_processing("", ctx):
        await profile.get_daily("", ctx=ctx, dc_id=ctx.author.user.id)
        delete_from_processing("", ctx)
    else:
        await ctx.send("Error! Please wait for the last command finish.")

@client.command(name="start")
async def c_start(message: Context):
    if store_to_processing(message):
        if blackjack.game_records.get(str(message.channel.id)):
            await message.channel.send("A game has started! Please wait for the next game.")
        else:
            embed = discord.Embed()
            embed.type = "rich"
            embed.set_author(name="A game is started! Use command \"!join\" to join this game. ")
            embed.set_footer(text=f"The game will start in {turn_count} second(s).")

            m = await message.channel.send(embed=embed)
            loop.create_task(blackjack.game_task(message.channel, m))
    else:
        await message.reply("Error! Please wait for the last command finish.")

@bot.command(name="bj_start", description="Start a BlackJack game", scope=guild_ids)
async def c__start(ctx: interactions.CommandContext):
    if store_to_processing("", ctx):
        channel = client.get_channel(id=int(ctx.channel_id))
        await channel.send("hi")
        # if blackjack.game_records.get(str(ctx.channel_id)):
        #     await message.channel.send("A game has started! Please wait for the next game.")
        # else:
        #     embed = discord.Embed()
        #     embed.type = "rich"
        #     embed.set_author(name="A game is started! Use command \"!join\" to join this game. ")
        #     embed.set_footer(text=f"The game will start in {turn_count} second(s).")

        #     m = await message.channel.send(embed=embed)
        #     loop.create_task(blackjack.game_task(message.channel, m))
        delete_from_processing("", ctx)
        await ctx.send("A game is staring...")
    else:
        await ctx.send("Error! Please wait for the last command finish.")

loop = asyncio.get_event_loop()
task2 = loop.create_task(client.start(token, bot=True))
task1 = loop.create_task(bot.start())

gathered = asyncio.gather(task1, task2, loop=loop)
loop.run_until_complete(gathered)

# bot.start()