import discord
from discord.ext import commands
from discord.commands import slash_command
from discord.ui import Button, View
import json
import random
import time
import asyncio
import os, shutil
from games.game_config import *
# from functions import help_center
import longman
# import functions.profile as profile
# from functions import help_center
# from functions.db_game import DB
# from games.blackjack import game_records
# from games import blackjack

with open("./token_dev.txt", "r", encoding="utf8") as f:
    token = f.read()

intents = discord.Intents.all()
# intents.messages = True

bot_s = discord.Bot() # slash command bot
bot_c = commands.Bot(command_prefix="bj!", intents=intents) # command bot
bot_s_is_ready = False
bot_c_is_ready = False
# hpc = help_center.helpCenter()

if not os.path.exists("./db_bj.db3"):
    shutil.copy("./db_bj2.db3", "./db_bj.db3")
    
guild_ids = [944092609066962975]
# guild_ids = None 

processing_channel = {}
processing_user = {}

initial_finished = False
# game_records = {}

def store_to_processing(message, ctx=None):
    if is_in_processing(message, ctx) or not initial_finished:
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

def delete_from_processing(message, ctx=None):
    if ctx:
        processing_channel.pop(str(ctx.channel_id))
        processing_user.pop(str(ctx.author.user.id))
    else:
        processing_channel.pop(str(message.channel.id))
        processing_user.pop(str(message.author.id))

def is_in_processing(message:commands.Context, ctx=None):
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

@bot_c.event
async def on_ready():
    global bot_c_is_ready
    bot_c_is_ready = True
    print(f"command bot is ready {bot_c.user}")

@bot_s.event
async def on_ready():
    global bot_s_is_ready
    bot_s_is_ready = True
    print("slash command bot is ready")

@bot_s.slash_command(name="test3", guild_ids=guild_ids)
async def hi4(ctx):
    await ctx.respond("HI")

@bot_c.command()
async def a(ctx):
    await ctx.send("ctest")


loop = asyncio.get_event_loop()
task2 = loop.create_task(bot_c.start(token))
task1 = loop.create_task(bot_s.start(token))


gathered = asyncio.gather(task1, task2, loop=loop)
loop.run_until_complete(gathered)

# bot_c.run(token)