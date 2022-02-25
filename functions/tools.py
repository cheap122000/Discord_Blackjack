import discord
from .db_game import DB
from discord.ext.commands import Bot
import time
from typing import Optional, Union
from discord.ext.commands.context import Context
from discord.commands.context import ApplicationContext
import asyncio
import json

bot = Bot(command_prefix="bj!", intents=discord.Intents.all())

processing_channel = {}
processing_user = {}

bot_is_ready = False
initial_finished = True

with open("./token_setting.json", "r", encoding="utf8") as f:
    setting = json.loads(f.read())

if setting["dev"]:
    with open("./token_dev.txt", "r", encoding="utf8") as f:
        token = f.read()
        guild_ids = setting["guild_ids"]
else:
    with open("./token.txt", "r", encoding="utf8") as f:
        token = f.read()
        guild_ids = None
# guild_ids = None 

loop = asyncio.get_event_loop()

def store_to_processing(ctx: Optional[Union[Context, ApplicationContext]]):
    if is_in_processing(ctx) or not bot_is_ready:
        return False
    else:
        # processing_channel[str(ctx.channel.id)] = int(time.time())
        processing_user[str(ctx.author.id)] = int(time.time())
        return True

def delete_from_processing(ctx: Optional[Union[Context, ApplicationContext]]):
    # processing_channel.pop(str(ctx.channel.id))
    processing_user.pop(str(ctx.author.id))

def is_in_processing(ctx: Optional[Union[Context, ApplicationContext]]):
    now_time = int(time.time())

    # p_time = processing_channel.get(str(ctx.channel.id))
    # if p_time:
    #     if now_time - p_time < 30:
    #         return True
    
    p_time = processing_user.get(str(ctx.author.id))
    if p_time:
        if now_time - p_time < 30:
            return True

    return False

async def send_message(ctx: Optional[Union[Context, ApplicationContext]], *args, **kwargs):
    if isinstance(ctx, Context):
        if kwargs.get("ephemeral"):
            return
        await ctx.send(*args, **kwargs)
    else:
        await ctx.respond(*args, **kwargs)

async def create_message(ctx: Optional[Union[Context, ApplicationContext]], *args, **kwargs):
    return await ctx.send(*args, **kwargs)

async def reply_message(ctx: Optional[Union[Context, ApplicationContext]], *args, **kwargs):
    if isinstance(ctx, Context):
        return await ctx.reply(*args, **kwargs)
    else:
        return await ctx.respond(*args, **kwargs)