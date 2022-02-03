import discord
import sqlite3
import json
import random
import time

client = discord.Client()

deck_of_card = {}
for i in range(52):
    temp = {}
    temp["number"] = i % 13
    temp["point"] = temp["number"] + 1 if temp["number"] + 1 < 11 else 0.5
    temp["number"] = "A" if temp["number"] == 0 else "J" if temp["number"] == 10 else "Q" if temp["number"] == 11 else "K" if temp["number"] == 12 else str(temp["number"] + 1)
    temp["suit"] = "spades" if i < 13 else "hearts" if i < 26 else "diamonds" if i < 39 else "clubs"
    deck_of_card[i] = temp

new_deck = [i for i in range(52)]
commands = ["!start", "!hit", "!surrender", "!reset"]
processing = {}

conn = sqlite3.connect("./card.db3")
c = conn.cursor()

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.lower() in commands:
        p_time = processing.get(f"{message.channel.id}")
        if p_time:
            if int(time.time()) - p_time < 10:
                return
        processing[f"{message.channel.id}"] = int(time.time())
    else:
        pass

    if message.content.lower() == "!hi":
        await message.channel.send(f"Hi <@!{message.author.id}>")

    if message.content.lower() == "!start":
        cursor = c.execute(f"SELECT * FROM games WHERE channel_id='{message.channel.id}'").fetchall()

        if len(cursor) > 0:
            await message.channel.send("This channel has already started a card game.")
        else:
            temp = {}
            c.execute(f"INSERT INTO games (channel_id, cards, records) VALUES ('{message.channel.id}', '{json.dumps(new_deck)}', '{json.dumps(temp)}')")
            conn.commit()
            await message.channel.send("A card game is started!")

    if message.content.lower() == "!hit":
        cursor = c.execute(f"SELECT * FROM games WHERE channel_id='{message.channel.id}'").fetchall()

        if len(cursor) == 0:
            await message.channel.send("This channel haven't started a card game, use the command \"!start\" to start a card game.")
        else:
            cards = json.loads(cursor[0][2])
            records = json.loads(cursor[0][3])
            rand_num = random.randint(0, len(cards)-1)
            hit = cards.pop(rand_num)

            id = str(message.author.id)
            if not records.get(id):
                records[id] = []
            records[id].append(hit)

            if len(cards) > 0:
                left_card = cards
            else:
                left_card = new_deck

            now_cards = ""
            points = 0
            for card in records[id]:
                now_cards += f"|:{deck_of_card[card]['suit']}:{deck_of_card[card]['number']}| "
                points += deck_of_card[card]['point']

            if points > 10.5:
                records[id] = []
                c.execute(f"UPDATE games SET cards='{json.dumps(left_card)}', records='{json.dumps(records)}' WHERE channel_id='{message.channel.id}'")
                conn.commit()
                await message.channel.send(f"<@!{message.author.id}> got a |:{deck_of_card[hit]['suit']}:{deck_of_card[hit]['number']}|\nNow have {now_cards}")
                await message.channel.send(f"<@!{message.author.id}> has busted! :bomb: :bomb: :bomb:")
                if left_card == new_deck: await message.channel.send(f"Cards has been drawn! Reset a new deck!")
            elif points == 10.5 or len(records[id]) == 5:
                records[id] = []
                c.execute(f"UPDATE games SET cards='{json.dumps(left_card)}', records='{json.dumps(records)}' WHERE channel_id='{message.channel.id}'")
                conn.commit()
                await message.channel.send(f"<@!{message.author.id}> got a |:{deck_of_card[hit]['suit']}:{deck_of_card[hit]['number']}|\nNow have {now_cards}")
                await message.channel.send(f"<@!{message.author.id}> won the game! :money_with_wings: :money_with_wings: :money_with_wings:")
                if left_card == new_deck: await message.channel.send(f"Cards has been drawn! Reset a new deck!")
            else:
                c.execute(f"UPDATE games SET cards='{json.dumps(left_card)}', records='{json.dumps(records)}' WHERE channel_id='{message.channel.id}'")
                conn.commit()
                await message.channel.send(f"<@!{message.author.id}> got a |:{deck_of_card[hit]['suit']}:{deck_of_card[hit]['number']}|\nNow have {now_cards}")
                if left_card == new_deck: await message.channel.send(f"Cards has been drawn! Reset a new deck!")

    if message.content.lower() == "!surrender":
        cursor = c.execute(f"SELECT * FROM games WHERE channel_id='{message.channel.id}'").fetchall()

        if len(cursor) == 0:
            await message.channel.send("This channel haven't started a card game, use the command \"!start\" to start a card game.")
        else:
            cards = json.loads(cursor[0][2])
            records = json.loads(cursor[0][3])

            id = str(message.author.id)
            if not records.get(id):
                records[id] = []
            records[id] = []

            c.execute(f"UPDATE games SET records='{json.dumps(records)}' WHERE channel_id='{message.channel.id}'")
            conn.commit()

            await message.channel.send(f"<@!{message.author.id}> has surrendered!")

    if message.content.lower() == "!reset":
        temp = {}
        c.execute(f"UPDATE games SET cards='{json.dumps(new_deck)}', records='{json.dumps(temp)}' WHERE channel_id='{message.channel.id}'")
        conn.commit()
        await message.channel.send("Game has been resetted!")

    if message.content.lower() in commands: processing.pop(f"{message.channel.id}")

with open("./token.txt", "r", encoding="utf8") as f:
    token = f.read()
client.run(token)