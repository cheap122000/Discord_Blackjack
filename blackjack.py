import discord
import json
import random
import time
from db_bj import DB
import asyncio
import os, shutil

client = discord.Client()

if not os.path.exists("./db_bj.db3"):
    shutil.copy("./db_bj2.db3", "./db_bj.db3")

with open("./token.txt", "r", encoding="utf8") as f:
    token = f.read()
    
commands = ["!start", "!hit", "!surrender", "!reset", "!daily"]
processing_channel = {}
processing_user = {}

def store_to_processing(message):
    processing_channel[str(message.channel.id)] = int(time.time())
    processing_user[str(message.author.id)] = int(time.time())

def delete_from_processing(message):
    processing_channel.pop(str(message.channel.id))
    processing_user.pop(str(message.author.id))

def is_in_processing(message):
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


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.find("<@!938461513834962944>") != -1:
        await message.channel.send(f"<@!{message.author.id}> 衝啥? 輸贏???")
        return

    if message.content.lower().startswith(tuple(commands)):
        if not is_in_processing(message):
            store_to_processing(message)
        else:
            await message.channel.send("Please wait for the last command finish.")
            return

    if message.content.lower().startswith("!daily"):
        db = DB()
        success, balance = db.get_daily(message.author.id)
        db.close()

        if success:
            await message.channel.send(f"<@!{message.author.id}> got daily 1000 Nicoins, now has {balance} Nicoins.")
        else:
            await message.channel.send(f"<@!{message.author.id}> had obtained daily Nicoins today, now has {balance} Nicoins.")

    if message.content.lower().startswith("!start"):
        db = DB()
        game_step, time_left = db.start_a_game(message.channel.id)
        if game_step:
            await message.channel.send("A game has started! Please wait for the next game.")
        else:
            await message.channel.send(f"A game is started! Use command \"!join\" to join this game. A game will start in {time_left} second(s).")
            client.loop.create_task(game_task(message.channel))
        db.close()

    if message.content.lower().startswith(tuple(commands)): delete_from_processing(message)

async def game_task(channel):
    print(f"HI {channel.id}")


async def my_background_task():
    db = DB()
    await client.wait_until_ready()
    # counter = 0
    # channel = client.get_channel(id=)
    while not client.is_closed():
        times_up = db.check_time()
        if len(times_up): print(times_up)
        await asyncio.sleep(5) # task runs every n seconds

client.loop.create_task(my_background_task())
client.run(token)