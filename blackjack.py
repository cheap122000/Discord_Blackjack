import discord
import json
import random
import time
from db import DB
import asyncio
import os, shutil

client = discord.Client()

if not os.path.exists("./blackjack.db3"):
    shutil.copy("./blackjack2.db3", "./blackjack.db3")

with open("./token.txt", "r", encoding="utf8") as f:
    token = f.read()

deck_of_card = {}
for i in range(52):
    temp = {}
    temp["number"] = i % 13
    temp["point"] = 10 if temp["number"] > 8 else 11 if temp["number"] == 0 else temp["number"] + 1
    temp["number"] = "A" if temp["number"] == 0 else "J" if temp["number"] == 10 else "Q" if temp["number"] == 11 else "K" if temp["number"] == 12 else str(temp["number"] + 1)
    temp["suit"] = "spades" if i < 13 else "hearts" if i < 26 else "diamonds" if i < 39 else "clubs"
    deck_of_card[i] = temp

new_deck = [i for i in range(52)]
commands = ["!start", "!hit", "!surrender", "!reset"]
processing = {}

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

async def my_background_task():
    await client.wait_until_ready()
    # counter = 0
    # channel = client.get_channel(id=)
    while not client.is_closed():
        
        await asyncio.sleep(60) # task runs every 60 seconds

client.loop.create_task(my_background_task())
client.run(token)