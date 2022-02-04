import discord
import json
import random
import time
from db import DB
import asyncio

client = discord.Client()

with open("./token.txt", "r", encoding="utf8") as f:
    token = f.read()

async def my_background_task():
    await client.wait_until_ready()
    # counter = 0
    # channel = client.get_channel(id=938896783269052437)
    while not client.is_closed():
        
        await asyncio.sleep(60) # task runs every 60 seconds

client.loop.create_task(my_background_task())
client.run(token)