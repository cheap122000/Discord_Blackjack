import discord
from discord.ext import commands
from discord.ext.commands.context import Context
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
from cogs import cog_profile, cog_blackjack, cog_gamble, cog_balance, cog_longman

token = tools.token

intents = discord.Intents.all()

bot = commands.Bot(command_prefix="bj!", intents=intents)
bot.remove_command("help")

hpc = help_center.helpCenter()

if not os.path.exists("./db_bj.db3"):
    shutil.copy("./db_bj2.db3", "./db_bj.db3")
    

@bot.event
async def on_ready():
    tools.bot_is_ready = True
    await bot.change_presence(activity=discord.Game(name="/help or bj!help"))
    print(f"bot is ready, login as {bot.user}")

# help
@bot.command(name="help")
async def c_help(ctx: Context):
    await tools.send_message(ctx, embed=hpc.set_help_center(message=ctx))

@bot.slash_command(name="help", description="Help Center", guild_ids=tools.guild_ids)
async def c__help(ctx: ApplicationContext):
    await tools.send_message(ctx, embed=hpc.set_help_center(None, ctx))


bot.add_cog(cog_profile.Profile(bot))
bot.add_cog(cog_blackjack.BJGame(bot))
bot.add_cog(cog_gamble.GambleGame(bot))
bot.add_cog(cog_balance.Balance(bot))
# bot.add_cog(cog_longman.LongMan(bot))

bot.run(token)