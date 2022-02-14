import discord
import json
import random
import time
from db_bj import DB
import asyncio
import os, shutil
from settings import *
import help_center
import longman

client = discord.Client()
hpc = help_center.helpCenter()

if not os.path.exists("./db_bj.db3"):
    shutil.copy("./db_bj2.db3", "./db_bj.db3")

with open("./token.txt", "r", encoding="utf8") as f:
    token = f.read()
    
processing_channel = {}
processing_user = {}

game_records = {}

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

    if message.content.lower().startswith("bj!help"):
        await message.channel.send(embed=hpc.set_help_center(message))
        return

    if message.content.find("<@!938461513834962944>") != -1:
        await message.channel.send(f"<@!{message.author.id}> 衝啥? 輸贏???")
        return

    if message.content.lower().startswith(tuple(commands)):
        if not is_in_processing(message):
            store_to_processing(message)
        else:
            await message.reply("Error! Please wait for the last command finish.")
            return

    if message.content.lower().startswith("bj!op"):
        channel_id = str(message.channel.id)
        try:
            m_s = message.content.lower().split(" ")
            if len(m_s) != 3:
                await message.channel.send("!op needs 2 parameter.")
                delete_from_processing(message)
                return
            if str(message.author.id) != "355354569049505792":
                await message.channel.send("You are not CodingMaster = =")
                delete_from_processing(message)
                return
            dc_id = m_s[1].replace("<@!", "").replace(">", "")
            give_amount = int(m_s[2])
        except:
            await message.channel.send("Your bet amount must be a positive number")
            delete_from_processing(message)
            return

        db = DB()
        balance = db.get_balance(dc_id, give_amount)
        db.close()
        
        await message.channel.send(f"<@!{dc_id}> now have {balance} :coin:")
    
    if message.content.lower() == "bj!pool":
        db = DB()
        prize = db.query_guild_pool(message.guild.id)
        db.close()

        embed = discord.Embed()
        embed.colour = discord.Colour.green()
        embed.set_author(name=f"This server's prize pool has {prize} Nicoins.", icon_url=message.guild.icon_url)
        await message.channel.send(embed=embed)
        return

    if message.content.lower().startswith("bj!longman"):
        await longman.longman(message)

    if message.content.lower().startswith("bj!gamble"):
        channel_id = str(message.channel.id)
        try:
            m_s = message.content.lower().split(" ")
            if len(m_s) != 2:
                await message.channel.send("!gamble needs 1 parameter.")
                delete_from_processing(message)
                return
            bet_amount = int(m_s[1])
            if bet_amount < 1:
                await message.channel.send("Your bet amount must be at least 1 Nicoins.")
                delete_from_processing(message)
                return
        except:
            await message.channel.send("Your bet amount must be a positive number")
            delete_from_processing(message)
            return

        embed = discord.Embed()
        embed.type = "rich"

        db = DB()
        success, balance = db.bet(message.author.id, bet_amount)
        if success:
            num = random.randint(1, 100)
            if num <= 60:
                embed.colour = discord.Colour.red()
                embed.set_author(name=f"{message.author.display_name} rolled {num}, lost {bet_amount} Nicoins. Now have {balance} Nicoins", icon_url=message.author.avatar_url)
            elif num <= 97:
                balance = db.get_balance(message.author.id, bet_amount*2)
                embed.colour = discord.Colour.green()
                embed.set_author(name=f"{message.author.display_name} rolled {num}, won {bet_amount} Nicoins. Now have {balance} Nicoins", icon_url=message.author.avatar_url)
            else:
                balance = db.get_balance(message.author.id, bet_amount*3)
                embed.colour = discord.Colour.gold()
                embed.set_author(name=f"{message.author.display_name} rolled {num}, won {bet_amount*2} Nicoins. Now have {balance} Nicoins", icon_url=message.author.avatar_url)
            await message.reply(embed=embed)
        else:
            await message.reply(content=f"You don't have enough Nicoins. Your balance: {balance} :coin:")
        db.close()

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
                delete_from_processing(message)
                return
            bet_amount = int(m_s[1])
            if bet_amount < 100:
                await message.channel.send("Your bet amount must be at least 100 Nicoins.")
                delete_from_processing(message)
                return
        except:
            await message.channel.send("Your bet amount must be at least 100 Nicoins.")
            delete_from_processing(message)
            return

        if game_records.get(channel_id):
            if game_records[channel_id]["step"] != 0:
                await message.reply(f"A game is started. Please wait for the next game.")
                delete_from_processing(message)
                return
            if len(game_records[channel_id]["players"]) < 6:
                db = DB()
                success, balance = db.bet(message.author.id, bet_amount)
                if success:
                    await message.reply(f"You joined the game, now you left {balance} Nicoins.")
                else:
                    await message.reply(f"You don't have enough Nicoins to bet. Your Nicoins: {balance}")
                    db.close()
                    delete_from_processing(message)
                    return
                db.close()
                game_records[channel_id]["players"].append({"user_id": message.author.id, "user_name": message.author.display_name, "bet_amount": bet_amount, "stand": False, "cards": [], "result": None})

                if async_delay > 2:
                    await step(game_records[channel_id])
            else:
                await message.channel.send("The max limit for a game is 6 players. Please wait for the next game.")
        else:
            await message.reply(f"Use command bj!start to create a game first.")

    if message.content.lower().startswith("bj!p"):
        db = DB()
        embed = discord.Embed()
        embed.type = "rich"
        embed.set_author(name=f"{message.author.display_name} has {db.query_user_balance(message.author.id)} Nicoins.", icon_url=message.author.avatar_url)
        embed.colour = discord.Colour.green()
        db.close()
        await message.channel.send(embed=embed)
    
    if message.content.lower().startswith("bj!hit"):
        channel_id = str(message.channel.id)

        if game_records.get(channel_id):
            turn = game_records[channel_id]["turn"]
            if game_records[channel_id]["step"] != 2 or game_records[channel_id]["players"][turn]["user_id"] != message.author.id:
                await message.reply(f"Not your turn.")
                delete_from_processing(message)
                return
            else:
                cards, points = show_cards(game_records[channel_id]["players"][turn]["cards"])
                if (len(game_records[channel_id]['players'][turn]["cards"]) < 5 or points < 21) and not game_records[channel_id]['players'][turn]["stand"]:
                    game_records[channel_id]['players'][turn]["cards"].append(hit_a_card(game_records[channel_id]['cards']))
                    game_records[channel_id]['hit'] = True
                else:
                    await message.reply("Invalid command.")
        else:
            await message.reply(f"Use command bj!start to create a game first.")

    if message.content.lower().startswith("bj!double"):
        channel_id = str(message.channel.id)

        if game_records.get(channel_id):
            turn = game_records[channel_id]["turn"]
            if game_records[channel_id]["step"] != 2 or game_records[channel_id]["players"][turn]["user_id"] != message.author.id:
                await message.reply(f"Not your turn.")
                delete_from_processing(message)
                return
            else:
                cards, points = show_cards(game_records[channel_id]["players"][turn]["cards"])
                if len(game_records[channel_id]['players'][turn]["cards"]) == 2 and points < 21 and not game_records[channel_id]['players'][turn]["stand"]:
                    game_records[channel_id]['start_time'] = int(time.time())
                    game_records[channel_id]['players'][turn]["stand"] = True
                    db = DB()
                    success, balance = db.bet(message.author.id, game_records[channel_id]['players'][turn]["bet_amount"])
                    if success:
                        await message.reply(f"You doubled, now you left {balance} Nicoins.")
                        game_records[channel_id]['players'][turn]["bet_amount"] *= 2
                    else:
                        await message.reply(f"You don't have enough Nicoins to double. Your Nicoins: {balance}")
                        db.close()
                        delete_from_processing(message)
                        return
                    db.close()

                    game_records[channel_id]['players'][turn]["cards"].append(hit_a_card(game_records[channel_id]['cards']))
                    game_records[channel_id]['hit'] = True
                else:
                    await message.reply("Invalid command.")
        else:
            await message.reply(f"Use command bj!start to create a game first.")

    if message.content.lower().startswith("bj!stand"):
        channel_id = str(message.channel.id)

        if game_records.get(channel_id):
            turn = game_records[channel_id]["turn"]
            if game_records[channel_id]["step"] != 2 or game_records[channel_id]["players"][turn]["user_id"] != message.author.id:
                await message.reply(f"Not your turn.")
                delete_from_processing(message)
                return
            else:
                cards, points = show_cards(game_records[channel_id]["players"][turn]["cards"])
                if (len(game_records[channel_id]['players'][turn]["cards"]) < 5 or points < 21):
                    game_records[channel_id]['hit'] = True
                    game_records[channel_id]['start_time'] = int(time.time()) - hit_count + 5
                    game_records[channel_id]['players'][turn]["stand"] = True
                else:
                    await message.reply("Invalid command.")
        else:
            await message.reply(f"Use command bj!start to create a game first.")

    if message.content.lower().startswith(tuple(commands)): delete_from_processing(message)

async def game_task(channel, m):
    # db = DB()
    channel_id = str(channel.id)
    if channel_id in game_records:
        await channel.send("A game has started! Please wait for the next game.")
        return
    game_records[channel_id] = {"players": [], "turn": -1, "hit":False, "dealer": {"cards": []}, "message": m, "start_time": int(time.time()), "step": 0, "record": {}, "cards": [i for i in range(52)]}

    while True:
        if game_records[channel_id]["step"] == 0:
            await step(game_records[channel_id])
        elif game_records[channel_id]["step"] == 1:
            game_records[channel_id]["dealer"]["cards"].append(hit_a_card(game_records[channel_id]["cards"]))
            await step1(game_records[channel_id])
        elif game_records[channel_id]["step"] == 2:
            await step2(game_records[channel_id])
        elif game_records[channel_id]["step"] == 3:
            await step3(game_records[channel_id])
        elif game_records[channel_id]["step"] == 4:
            await step4(game_records[channel_id])


        if game_records[channel_id]["step"] == 5:
            game_records.pop(channel_id)
            break
        # db.save_game(channel_id, game_records[channel_id])
        # print(game_records[channel_id]["step"])
        await asyncio.sleep(async_delay)
    
    # db.close()

async def step(record):
    time_left = turn_count - (int(time.time()) - record['start_time'])
    time_left = 0 if time_left < 0 else time_left
    embed = discord.Embed()
    embed.type = "rich"
    embed.set_author(name="A game is started! Use command \"bj!join\" to join this game. ")
    embed.set_footer(text=f"The game will start in {time_left} second(s).")
    embed.colour = discord.Colour.orange() 

    dealer_cards, dealer_points = show_cards(record["dealer"]["cards"])

    embed.add_field(name="Dealer", value=f"cards: {dealer_cards}", inline=False)

    for item in record["players"]:
        embed.add_field(name=item["user_name"], value=f"chips: {item['bet_amount']} :coin:\ncards: ", inline=False)

    if time_left <= 0:
        record["step"] += 1

    await record["message"].edit(embed=embed)

async def step1(record):
    embed = discord.Embed()
    embed.type = "rich"
    embed.colour = discord.Colour.orange() 
    n_players = len(record["players"])

    dealer_cards, dealer_points = show_cards(record["dealer"]["cards"])
    record['start_time'] = int(time.time()-50)
    content = f"Dealer got a {dealer_cards}"
    embed.set_author(name="It's dealer's turn.")
    embed.set_footer(text=f"The game is playing.")
    embed.add_field(name=":point_right: Dealer", value=f"cards: {dealer_cards}", inline=False)

    if n_players == 0:
        record["step"] = 5
        return
        
    for i, item in enumerate(record["players"]):
        embed.add_field(name=item["user_name"], value=f"chips: {item['bet_amount']} :coin:\ncards: ", inline=False)
    await record["message"].edit(embed=embed, content=content)

    embed.set_field_at(0, name="Dealer", value=f"cards: {dealer_cards}", inline=False)
    for _ in range(2):
        for i in range(n_players):
            await asyncio.sleep(1)
            record["players"][i]["cards"].append(hit_a_card(record["cards"]))
            
            if i == 0:
                ix = n_players - 1
                cards, points = show_cards(record["players"][ix]["cards"])
                embed.set_field_at(ix+1, name=f"{record['players'][ix]['user_name']}", value=f"chips: {record['players'][ix]['bet_amount']} :coin:\ncards: {cards}", inline=False)
            else:
                ix = i - 1
                cards, points = show_cards(record["players"][ix]["cards"])
                embed.set_field_at(ix+1, name=f"{record['players'][ix]['user_name']}", value=f"chips: {record['players'][ix]['bet_amount']} :coin:\ncards: {cards}", inline=False)
            
            cards, points = show_cards(record["players"][i]["cards"])
            embed.set_field_at(i+1, name=f":point_right: {record['players'][i]['user_name']}", value=f"chips: {record['players'][i]['bet_amount']} :coin:\ncards: {cards}", inline=False)
            embed.set_author(name=f"It's {record['players'][i]['user_name']}'s turn.")
            content = f"<@!{record['players'][i]['user_id']}> got {cards}"
            await record["message"].edit(embed=embed, content=content)

    await asyncio.sleep(1)
    embed.set_field_at(n_players, name=f"{record['players'][n_players - 1]['user_name']}", value=f"chips: {record['players'][n_players - 1]['bet_amount']} :coin:\ncards: {cards}", inline=False)
    await record["message"].edit(embed=embed, content=None)

    record["step"] += 1

async def step2(record):
    embed = discord.Embed()
    embed.type = "rich"
    embed.colour = discord.Colour.orange() 

    for i, p in enumerate(record["players"]):
        record['turn'] = i
        cards, points = show_cards(p["cards"])

        # if i > 0:
        #     record["message"].embeds[0].set_field_at(i, name=f"{record['players'][i]['user_name']}", value=f"chips: {record['players'][i]['bet_amount']} :coin:\ncards: {cards}", inline=False)
        #     await record["message"].edit(embed=record["message"].embeds[0], content=f"{p['user_name']}'s turn.")

        record["message"].embeds[0].set_field_at(i+1, name=f":point_right: {record['players'][i]['user_name']}", value=f"chips: {record['players'][i]['bet_amount']} :coin:\ncards: {cards}", inline=False)
        await record["message"].edit(embed=record["message"].embeds[0], content=f"{p['user_name']}'s turn.")
        m = await record["message"].channel.send(f"<@!{p['user_id']}>'s turn. bj!stand / bj!hit / bj!double\nYour chips: {record['players'][i]['bet_amount']} :coin:. Your card(s): {cards}\nYou left {hit_count} second(s).")
        record["message2"] = m

        record['start_time'] = int(time.time())
        mem = 0
        while True:
            if record["players"][i]["stand"]:
                time_left = 5 - (int(time.time()) - record['start_time'])
            else:
                time_left = hit_count - (int(time.time()) - record['start_time'])
            time_left2 = time_left
            time_left = 0 if time_left < 0 else time_left

            if mem != time_left:
                mem = time_left if time_left > 0 else 0
                cards, points = show_cards(p["cards"])
                if record["hit"]:
                    record['start_time'] = int(time.time())
                    record["hit"] = False
                    await record["message2"].delete()
                    record["message2"] = None
                    time_left = hit_count

                if points > 21:
                    msg = f"<@!{record['players'][i]['user_id']}>'s turn is over.\nYour chips: {record['players'][i]['bet_amount']} :coin:. Your card(s): {cards}\nYou are busted :bomb::bomb::bomb:.\n{time_left} sencond(s) for the next player."
                    record["players"][i]["result"] = "busted"
                    record["players"][i]["stand"] = True
                elif len(record["players"][i]["cards"]) == 2 and points == 21:
                    msg = f"<@!{record['players'][i]['user_id']}>'s turn is over.\nYour chips: {record['players'][i]['bet_amount']} :coin:. Your card(s): {cards}\nYou got Black Jack :money_with_wings::money_with_wings::money_with_wings:\n{time_left} sencond(s) for the next player."
                    record["players"][i]["result"] = "bj"
                    record["players"][i]["stand"] = True
                elif len(record["players"][i]["cards"]) == 5:
                    msg = f"<@!{record['players'][i]['user_id']}>'s turn is over.\nYour chips: {record['players'][i]['bet_amount']} :coin:. Your card(s): {cards}\nYou got Five-card :flower_playing_cards::flower_playing_cards::flower_playing_cards:\n{time_left} sencond(s) for the next player."
                    record["players"][i]["result"] = "five"
                    record["players"][i]["stand"] = True
                elif points == 21:
                    record["players"][i]["result"] = "21"
                    msg = f"<@!{record['players'][i]['user_id']}>'s turn is over.\nYour chips: {record['players'][i]['bet_amount']} :coin:. Your card(s): {cards}\nYou got Twenty-One!!!\n{time_left} sencond(s) for the next player."
                    record["players"][i]["stand"] = True
                else:
                    if len(p["cards"]) == 2:
                        msg = f"<@!{record['players'][i]['user_id']}>'s turn. bj!stand / bj!hit / bj!double\nYour chips: {record['players'][i]['bet_amount']} :coin:. Your card(s): {cards}\nYou left {time_left} second(s)."
                    else:
                        msg = f"<@!{record['players'][i]['user_id']}>'s turn. bj!stand / bj!hit\nYour chips: {record['players'][i]['bet_amount']} :coin:. Your card(s): {cards}\nYou left {time_left} second(s)."

                if record["message2"]:
                    await record["message2"].edit(content=msg)
                else:
                    record['start_time'] = int(time.time())
                    record["message2"] = await record["message"].channel.send(msg)
                    
                
                record["message"].embeds[0].set_field_at(i+1, name=f":point_right: {record['players'][i]['user_name']}", value=f"chips: {record['players'][i]['bet_amount']} :coin:\ncards: {cards}", inline=False)
                await record["message"].edit(embed=record["message"].embeds[0], content=f"{record['players'][i]['user_name']}'s turn.")

            await asyncio.sleep(0.8)
            if time_left2 < 1.6:
                record["message"].embeds[0].set_field_at(i+1, name=f"{record['players'][i]['user_name']}", value=f"chips: {record['players'][i]['bet_amount']} :coin:\ncards: {cards}", inline=False)
                await record["message"].edit(embed=record["message"].embeds[0], content=f"{record['players'][i]['user_name']}'s turn.")
                break
    record["step"] += 1

async def step3(record):
    cards, points = show_cards(record["dealer"]["cards"])
    embed = record["message"].embeds[0]
    channel = record["message"].channel
    embed.set_field_at(0, name=f":point_right: Dealer", value=f"cards: {cards}", inline=False)
    embed.set_author(name=f"It's Dealer's turn.")
    await record["message"].edit(embed=embed, content="Dealer's turn.")
    record["message2"] = None

    while points < 17 and len(record["dealer"]["cards"]) < 5:
        await asyncio.sleep(1.5)
        record["dealer"]["cards"].append(hit_a_card(record["cards"]))
        cards, points = show_cards(record["dealer"]["cards"])
        embed.set_field_at(0, name=f":point_right: Dealer", value=f"cards: {cards}", inline=False)
        await record["message"].edit(embed=embed, content="Dealer's turn.")

        if record["message2"]:
            await record["message2"].edit(content=f"Dealer's turn. Dealer's cards: {cards}")
        else:
            record["message2"] = await channel.send(f"Dealer's turn. Dealer's cards: {cards}")

    embed.set_field_at(0, name=f"Dealer", value=f"cards: {cards}", inline=False)
    await record["message"].edit(embed=embed, content="Dealer's turn.")

    record["step"] += 1

async def step4(record):
    await asyncio.sleep(1)
    embed = record["message"].embeds[0]
    embed.set_author(name=f"Game's Result")
    embed.colour = discord.Colour.green()
    embed.set_footer(text="The game is over.")

    cards, points = show_cards(record["dealer"]["cards"])
    dealer_result = show_result(record["dealer"]["cards"], points)
    embed.set_field_at(0, name=f"Dealer", value=f"cards: {cards}\nresult: {dealer_result}", inline=False)

    temp = {}
    for i, p in enumerate(record["players"]):
        cards, points = show_cards(p["cards"])
        result = show_result(p["cards"], points)

        if result == "Black Jack":
            if dealer_result == "Black Jack":
                balance = 0
            else:
                balance = p["bet_amount"] * 1.5
        elif result == "Five-card":
            if dealer_result == "Five-card":
                balance = 0
            elif dealer_result == "Black Jack":
                balance = p["bet_amount"] * -1.5
            else:
                balance = p["bet_amount"] * 1.25
        elif result == "Busted":
            if dealer_result == "Black Jack":
                balance = p["bet_amount"] * -1.5
            else:
                balance = p["bet_amount"] * -1
        else:
            if dealer_result == "Black Jack":
                balance = p["bet_amount"] * -1.5
            elif dealer_result == "Five-card":
                balance = p["bet_amount"] * -1
            elif dealer_result == "Busted":
                balance = p["bet_amount"]
            else:
                if int(result) == int(dealer_result):
                    balance = 0
                elif int(result) > int(dealer_result):
                    balance = p["bet_amount"]
                else:
                    balance = p["bet_amount"] * -1
        balance = int(balance) + p["bet_amount"]

        id = str(p["user_id"])
        if temp.get(id):
            temp[id]["balance"] += balance
            temp[id]["profit"] += balance - p["bet_amount"]
        else:
            temp[id] = {}
            temp[id]["balance"] = balance
            temp[id]["profit"] = balance - p["bet_amount"]
            temp[id]["user_name"] = p["user_name"]


        embed.set_field_at(i+1, name=p["user_name"], value=f"chips: {record['players'][i]['bet_amount']} :coin:\ncards: {cards}\nresult: {result}\nbalance: {balance - p['bet_amount']} :coin:", inline=False)

    # await record["message"].edit(embed=embed, content="Result")
    all_balance = ""
    db = DB()
    for item in temp:
        if temp[item]["profit"] >= 0:
            b = db.get_balance(item, int(temp[item]['balance']))
            all_balance += f"<@!{item}> won {temp[item]['profit']} :coin:, now have {b} :coin:\n"
        else:
            b = db.get_balance(item, int(temp[item]['balance']))
            all_balance += f"<@!{item}> lost {temp[item]['profit']} :coin:, now have {b} :coin:\n"    
    db.close()
    await record["message"].channel.send(embed=embed, content=f"Result:\n{all_balance}")

    record["step"] += 1

def show_cards(cards: list):
    now_cards = ""
    points = 0
    a_count = 0
    for card in cards:
        now_cards += f"|:{deck_of_card[card]['suit']}:{deck_of_card[card]['number']}| "
        points += deck_of_card[card]['point']
        if deck_of_card[card]['point'] == 11:
            a_count += 1
    for _ in range(a_count):
        points = points - 10 if points > 21 else points
    return now_cards, points
        
def show_result(cards:list, points:int):
    if len(cards) == 2 and points == 21:
        return "Black Jack"
    elif len(cards) == 5 and points <= 21:
        return "Five-card"
    elif points > 21:
        return "Busted"
    else:
        return str(points) 

def hit_a_card(cards: list):
    rand_num = random.randint(0, len(cards)-1)
    hit = cards.pop(rand_num)
    # card = f"|:{deck_of_card[hit]['suit']}:{deck_of_card[hit]['number']}| "
    return hit

client.run(token)