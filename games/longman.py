from .game_config import *
import asyncio
import time
import discord
import random
from functions.db_game import DB
from discord.ui import Button, View, button, Modal, InputText
from discord import ButtonStyle

game_records = {}
turn_count = 30
seats = 10

player_init = {}

class Hit_Modal(Modal):
    def __init__(self, text) -> None:
        super().__init__(text)
        self.add_item(InputText(label="chips", placeholder="chips", value="100", style=discord.InputTextStyle.short))
    
    async def callback(self, interaction: discord.Interaction):
        try:
            chips = int(self.children[0].value)
            if chips < 1:
                await interaction.response.send_message("You must input a positive integer!", view=LM_View(), ephemeral=True)
            else:
                guild_id = str(interaction.guild.id)
                await interaction.response.send_message("success", ephemeral=True, delete_after=1)
        except:
            # await interaction.response.send_modal(Hit_Modal("123"))
            await interaction.response.send_message("You must input a positive integer!", view=LM_View(), ephemeral=True)


class LM_View(View):
    @button(label="Show card", style=ButtonStyle.primary, emoji="👀")
    async def show_callback(self, button: discord.Button, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        if game_records.get(guild_id):
            turn = game_records[guild_id]["turn"]
            if game_records[guild_id]["step"] != 2 or game_records[guild_id]["players"][turn]["user_id"] != interaction.user.id:
                await interaction.response.send_message(f"Not your turn.", delete_after=1, ephemeral=True)
                return
            else:
                cards, points = show_cards(game_records[guild_id]["players"][turn], force_show=True)
                if len(game_records[guild_id]['players'][turn]["cards"]) < 3:
                    await interaction.response.send_message(f"Your card is {cards}.\nWhat do you want to do?", ephemeral=True)
                else:
                    await interaction.response.send_message("Invalid command.", delete_after=1, ephemeral=True)
        else:
            await interaction.response.send_message(f"Use command `/lm_start` or `bj!lm_start` to create a game first.", delete_after=1)

    @button(label="Hit", style=ButtonStyle.green, emoji="✋")
    async def hit_callback(self, button: discord.Button, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        # await interaction.response.send_message("Invalid command.", ephemeral=True)
        await interaction.response.send_modal(Hit_Modal("How many chips you want to shoot?"))

    @button(label="Stand", style=ButtonStyle.red, emoji="🛑")
    async def stand_callback(self, button: discord.Button, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        await interaction.response.send_message("OK", ephemeral=True, delete_after=1)

async def game_task(channel, guild_id, m):
    if guild_id in game_records:
        await channel.send("A server can only create a LongMan game in the same time, please wait for the last game has been finished.")
        return
    db = DB()
    game_records[guild_id] = {"players": [], "turn": -1, "message": m, "start_time": int(time.time()), "prize": db.query_guild_pool(guild_id), "step": 0, "record": {}, "cards": [i for i in range(52)]}
    db.close()
    while True:
        if game_records[guild_id]["step"] == 0:
            await step(game_records[guild_id])
        if game_records[guild_id]["step"] == 1:
            await step1(game_records[guild_id])
        if game_records[guild_id]["step"] == 2:
            await step2(game_records[guild_id])

        await asyncio.sleep(async_delay)

async def step(record):
    time_left = turn_count - (int(time.time()) - record['start_time'])
    time_left = 0 if time_left < 0 else time_left
    embed = discord.Embed()
    embed.type = "rich"
    embed.set_author(name="A LongMan game is started! Use command `bj!lm_join` or `/lm_join` to join this game. ")
    seats_left = seats - len(record["players"])
    embed.set_footer(text=f"The game will start in {time_left} second(s), {seats_left} seats left.")
    embed.colour = discord.Colour.orange() 

    prize = record["prize"]
    embed.add_field(name="Prize Pool", value=f"{prize} :coin:", inline=False)

    for item in record["players"]:
        embed.add_field(name=item["user_name"], value=f"chips: {item['bet_amount']} :coin:\ncards: ", inline=False)

    if time_left <= 0:
        record["step"] += 1

    await record["message"].edit(embed=embed)
    record["message"].embeds[0] = embed

async def step1(record):
    # longman.game_records[channel_id]["players"].append({"user_id": ctx.author.id, "user_name": ctx.author.display_name, "bet_amount": 0, "cards": [], "revealed": False, "result": None})
    embed = discord.Embed()
    embed.type = "rich"
    embed.colour = discord.Colour.orange() 
    content = "Game start!"
    n_players = len(record["players"])

    record['start_time'] = int(time.time()-50)

    prize = record["prize"]
    embed.add_field(name="Prize Pool", value=f"{prize} :coin:", inline=False)

    if n_players == 0:
        record["step"] = 5
        return
    
    for i, item in enumerate(record["players"]):
        embed.add_field(name=item["user_name"], value=f"chips: {item['bet_amount']} :coin:\ncards: ", inline=False)

    await record["message"].delete()
    # await record["message"].edit(embed=embed, content=content)
    record["message"] = await record["message"].channel.send(embed=embed, content=content)

    for _ in range(2):
        for i in range(n_players):
            await asyncio.sleep(1)
            record["players"][i]["cards"].append(hit_a_card(record["cards"]))
            
            # delete the point finger
            if i == 0:
                ix = n_players - 1
                cards, points = show_cards(record["players"][ix])
                embed.set_field_at(ix+1, name=f"{record['players'][ix]['user_name']}", value=f"chips: {record['players'][ix]['bet_amount']} :coin:\ncards: {cards}", inline=False)
            else:
                ix = i - 1
                cards, points = show_cards(record["players"][ix])
                embed.set_field_at(ix+1, name=f"{record['players'][ix]['user_name']}", value=f"chips: {record['players'][ix]['bet_amount']} :coin:\ncards: {cards}", inline=False)
            
            cards, points = show_cards(record["players"][i])
            embed.set_field_at(i+1, name=f":point_right: {record['players'][i]['user_name']}", value=f"chips: {record['players'][i]['bet_amount']} :coin:\ncards: {cards}", inline=False)
            embed.set_author(name=f"It's {record['players'][i]['user_name']}'s turn.")
            content = f"<@!{record['players'][i]['user_id']}> got {cards}"
            await record["message"].edit(embed=embed, content=content)

    await asyncio.sleep(1)
    embed.set_field_at(n_players, name=f"{record['players'][n_players - 1]['user_name']}", value=f"chips: {record['players'][n_players - 1]['bet_amount']} :coin:\ncards: {cards}", inline=False)
    await record["message"].edit(embed=embed, content=None)
    record["message"].embeds[0] = embed

    record["step"] += 1

async def step2(record):
    await record["message"].edit(view=LM_View())

def show_cards(player, force_show=False):
    now_cards = ""
    for card in player["cards"]:
        if player["revealed"] or force_show:
            now_cards += f"|:{deck_of_card[card]['suit']}:{deck_of_card[card]['number']}| "
        else:
            now_cards += "|:question:| "

    return now_cards, None

def hit_a_card(cards: list):
    rand_num = random.randint(0, len(cards)-1)
    hit = cards.pop(rand_num)
    # card = f"|:{deck_of_card[hit]['suit']}:{deck_of_card[hit]['number']}| "
    return hit