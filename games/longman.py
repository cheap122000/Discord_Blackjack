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
    @button(label="Hit", style=ButtonStyle.green, emoji="✋")
    async def hit_callback(self, button: discord.Button, interaction: discord.Interaction):
        channel_id = str(interaction.channel.id)
        # await interaction.response.send_message("Invalid command.", ephemeral=True)
        await interaction.response.send_modal(Hit_Modal("How many chips you want to shoot?"))

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

    await record["message"].edit(embed=embed, view=LM_View())
    record["message"].embeds[0] = embed

async def step1(record):
    # longman.game_records[channel_id]["players"].append({"user_id": ctx.author.id, "user_name": ctx.author.display_name, "bet_amount": 0, "cards": [], "result": None})
    embed = discord.Embed()
    embed.type = "rich"
    embed.colour = discord.Colour.orange() 
    n_players = len(record["players"])

    record['start_time'] = int(time.time()-50)