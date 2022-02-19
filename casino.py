import discord
from discord.ext import commands
from discord.ext.commands.context import Context
from discord.commands import slash_command
from discord.commands.context import ApplicationContext
from discord.ui import Button, View
import json
import random
import time
import asyncio
import os, shutil
from games.game_config import *
from functions import help_center, tools
import longman
from cogs import cog_profile
# import functions.profile as profile
# from functions import help_center
# from functions.db_game import DB
# from games.blackjack import game_records
# from games import blackjack

with open("./token_dev.txt", "r", encoding="utf8") as f:
    token = f.read()

intents = discord.Intents.all()

bot_s = discord.Bot() # slash command bot
bot_c = commands.Bot(command_prefix="bj!", intents=intents) # command bot
bot_c.remove_command("help")

hpc = help_center.helpCenter()

if not os.path.exists("./db_bj.db3"):
    shutil.copy("./db_bj2.db3", "./db_bj.db3")
    

@bot_c.event
async def on_ready():
    tools.bot_c_is_ready = True
    print(f"command bot is ready {bot_c.user}")

@bot_s.event
async def on_ready():
    tools.bot_s_is_ready = True
    print("slash command bot is ready")

# help
@bot_c.command(name="help")
async def c_help(message: Context):
    print(type(message))
    await message.channel.send(embed=hpc.set_help_center(message))

@bot_s.slash_command(name="help", description="Help Center", guild_ids=tools.guild_ids)
async def c__help(ctx: ApplicationContext):
    await ctx.respond(embed=hpc.set_help_center(None, ctx))


bot_c.add_cog(cog_profile.c_profile(bot_c))
bot_s.add_cog(cog_profile.s_profile(bot_s))

loop = asyncio.get_event_loop()
task2 = loop.create_task(bot_c.start(token))
task1 = loop.create_task(bot_s.start(token))


gathered = asyncio.gather(task1, task2, loop=loop)
loop.run_until_complete(gathered)