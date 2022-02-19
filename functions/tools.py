from .db_game import DB
from discord.ext.commands import Bot
import time
from discord.ext.commands.context import Context
from discord.commands.context import ApplicationContext

processing_channel = {}
processing_user = {}

bot_s_is_ready = False
bot_c_is_ready = False
initial_finished = True

guild_ids = [944092609066962975]
# guild_ids = None 

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

def is_in_processing(message:Context, ctx=None):
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