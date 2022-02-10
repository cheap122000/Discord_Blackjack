import discord
import json
import random
import time
from db_bj import DB
import asyncio
import os, shutil

client = discord.Client()

deck_of_card = {}
for i in range(52):
    temp = {}
    temp["number"] = i % 13
    temp["point"] = 10 if temp["number"] > 8 else 11 if temp["number"] == 0 else temp["number"] + 1
    temp["number"] = "A" if temp["number"] == 0 else "J" if temp["number"] == 10 else "Q" if temp["number"] == 11 else "K" if temp["number"] == 12 else str(temp["number"] + 1)
    temp["suit"] = "spades" if i < 13 else "hearts" if i < 26 else "diamonds" if i < 39 else "clubs"
    deck_of_card[i] = temp

new_deck = [i for i in range(52)]

if not os.path.exists("./db_bj.db3"):
    shutil.copy("./db_bj2.db3", "./db_bj.db3")

with open("./token.txt", "r", encoding="utf8") as f:
    token = f.read()
    
commands = ["bj!start", "bj!hit", "bj!surrender", "bj!reset", "bj!daily"]
processing_channel = {}
processing_user = {}

game_records = {}
turn_count = 60

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
async def on_message(message:discord.Message):
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

    if message.content.lower() == "!test":
        embed = discord.Embed()
        embed.type = "rich"
        embed.set_footer(text="DarkKnight_NVD#8388\uff0e\u4f7f\u7528 z!help [\u6307\u4ee4\u540d\u7a31] \u7372\u5f97\u66f4\u8a73\u7d30\u7684\u8aaa\u660e")
        await message.channel.send(embed=embed)

    if message.content.lower().startswith("bj!daily"):
        db = DB()
        success, balance = db.get_daily(message.author.id)
        db.close()

        if success:
            embed = discord.Embed()
            embed.type = "rich"
            embed.colour = discord.Colour.green()
            embed.set_footer(text=f"{message.author.display_name} got daily 1000 Nicoins, now has {balance} Nicoins.", icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)
        else:
            embed = discord.Embed()
            embed.type = "rich"
            embed.colour = discord.Colour.red()
            embed.set_footer(text=f"{message.author.display_name} had obtained daily Nicoins today, now has {balance} Nicoins", icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)

    if message.content.lower().startswith("bj!start"):
        db = DB()
        # game_step, time_left = db.start_a_game(message.channel.id)
        if game_records.get(str(message.channel.id)):
            await message.channel.send("A game has started! Please wait for the next game.")
        else:
            embed = discord.Embed()
            embed.type = "rich"
            embed.set_author(name="A game is started! Use command \"!join\" to join this game. ")
            embed.set_footer(text=f"The game will start in 60 second(s).")

            m = await message.channel.send(embed=embed)
            client.loop.create_task(game_task(message.channel, m))
        db.close()

    if message.content.lower().startswith("bj!join"):
        channel_id = str(message.channel.id)
        try:
            m_s = message.content.lower().split(" ")
            if len(m_s) != 2:
                await message.channel.send("bj!join needs 1 parameter.")
                return
            bet_amount = int(m_s[1])
            if bet_amount < 100:
                await message.channel.send("Your bet amount must be at least 100 Nicoins.")
                return

            db = DB()
            balance = db.query_user_balance(message.author.id)
            if bet_amount > balance:
                await message.channel.send(f"You don't have enough Nicoins to bet. Your Nicoins: {balance}")
                return
            db.close()
        except:
            await message.channel.send("Your bet amount must be at least 100 Nicoins.")
            return

        if game_records.get(channel_id):
            if len(game_records[channel_id]["players"]) < 6:
                game_records[channel_id]["players"].append({"user_id": message.author.id, "user_name": message.author.display_name, "bet_amount": bet_amount})

                await step0(game_records[channel_id])
            else:
                await message.channel.send("The max limit for a game is 6 players. Please wait for the next game.")

    if message.content.lower().startswith(tuple(commands)): delete_from_processing(message)

async def game_task(channel, m):
    # db = DB()
    channel_id = str(channel.id)
    if channel_id in game_records:
        await channel.send("A game has started! Please wait for the next game.")
        return
    game_records[channel_id] = {"players": [], "dealer": {}, "message": m, "start_time": int(time.time()), "step": 0, "record": {}, "cards": new_deck}

    while True:
        if game_records[channel_id]["step"] == 0:
            # TODO add players' field
            await step0(game_records[channel_id])
        elif game_records[channel_id]["step"] == 1:
            # TODO
            pass



        if game_records[channel_id]["step"] == 10:
            game_records.pop(channel_id)
            break
        # db.save_game(channel_id, game_records[channel_id])
        # print(game_records[channel_id]["step"])
        await asyncio.sleep(5)
    
    # db.close()

async def step0(record):
    time_left = turn_count - (int(time.time()) - record['start_time'])
    time_left = 0 if time_left < 0 else time_left
    embed = discord.Embed()
    embed.type = "rich"
    embed.set_author(name="A game is started! Use command \"!join\" to join this game. ")
    embed.set_footer(text=f"The game will start in {time_left} second(s).")
    ret = f"A game is started! Use command \"!join\" to join this game. The game will start in {time_left} second(s)."
    if len(record["players"]):
        ret += "\nPlayers:"
        for item in record["players"]:
            ret += f"\n{item['user_name']}: {item['bet_amount']} :money_with_wings:"

    if time_left <= 0:
        record["step"] += 1

    # await record["message"].edit(content=ret)
    await record["message"].edit(embed=embed, content=None)


def hit_a_card(cards: list):
    rand_num = random.randint(0, len(cards)-1)
    hit = cards.pop(rand_num)
    # card = f"|:{deck_of_card[hit]['suit']}:{deck_of_card[hit]['number']}| "
    return hit

client.run(token)