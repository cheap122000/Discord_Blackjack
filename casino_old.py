import discord
from discord.ext.commands import Bot, Context
import interactions
from discord.ui import Button, View
# from interactions import Button, ButtonStyle
import json
import random
import time
import asyncio
import os, shutil
from games.game_config import *
# from functions import help_center
import longman
# import functions.profile as profile
from functions import profile, tools, help_center
from functions.db_game import DB
from games.blackjack import game_records
from games import blackjack

with open("./token_dev.txt", "r", encoding="utf8") as f:
    token = f.read()

bot = interactions.Client(token)
# client = discord.ext.commands.Bot(command_prefix="bj!")
client = Bot(command_prefix="bj!")
client.remove_command("help")
hpc = help_center.helpCenter()

if not os.path.exists("./db_bj.db3"):
    shutil.copy("./db_bj2.db3", "./db_bj.db3")
    
guild_ids = [943730455755235339]
# guild_ids = None 

processing_channel = {}
processing_user = {}

initial_finished = False
# game_records = {}

def store_to_processing(message, ctx:interactions.CommandContext=None):
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

def delete_from_processing(message, ctx:interactions.CommandContext=None):
    if ctx:
        processing_channel.pop(str(ctx.channel_id))
        processing_user.pop(str(ctx.author.user.id))
    else:
        processing_channel.pop(str(message.channel.id))
        processing_user.pop(str(message.author.id))

def is_in_processing(message:Context, ctx:interactions.CommandContext=None):
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

def get_ctx_icon(ctx:interactions.CommandContext):
    return f"https://cdn.discordapp.com/avatars/{ctx.author.user.id}/{ctx.author.avatar}.webp?size=1024"

def get_ctx_display_name(ctx:interactions.CommandContext):
    return ctx.author.nick if ctx.author.nick else ctx.author.user.username

@client.event
async def on_ready():
    global initial_finished
    initial_finished = True
    print(f"Logged in as {client.user}")

@client.event
async def on_guild_join(guild):
    tools.add_guild_to_db(guild.id)

@bot.event
async def on_ready():
    print("Interactions ready")

# help
@client.command(name="help")
async def c_help(message: Context):
    await message.channel.send(embed=hpc.set_help_center(message))

@bot.command(name="help", description="Help Center", scope=guild_ids)
async def c__help(ctx: interactions.CommandContext):
    await ctx.send(embeds=hpc.set_help_center("", ctx))

# profile
@client.command(name="p")
async def c_profile(message: Context):
    if store_to_processing(message):
        embed = profile.get_profile(message, ctx=None, dc_id=message.author.id)
        await message.channel.send(embed=embed)
        delete_from_processing(message)
    else:
        await message.reply("Error! Please wait for the last command finish.")

@bot.command(name="profile", description="Show your profile", scope=guild_ids)
async def c__profile(ctx: interactions.CommandContext):
    if store_to_processing("", ctx):
        embed = profile.get_profile("", ctx=ctx, dc_id=ctx.author.user.id)
        await ctx.send(embeds=embed)
        delete_from_processing("", ctx)
    else:
        await ctx.send("Error! Please wait for the last command finish.")

#daily
@client.command(name="daily")
async def c_daily(message: Context):
    if store_to_processing(message):
        await profile.get_daily(message, ctx=None, dc_id=message.author.id)
        delete_from_processing(message)
    else:
        await message.reply("Error! Please wait for the last command finish.")

@bot.command(name="daily", description="Obtain daily 1000 Nicoins", scope=guild_ids)
async def c__daily(ctx: interactions.CommandContext):
    if store_to_processing("", ctx):
        await profile.get_daily("", ctx=ctx, dc_id=ctx.author.user.id)
        delete_from_processing("", ctx)
    else:
        await ctx.send("Error! Please wait for the last command finish.")

# BlackJack
## bj!start
@client.command(name="start")
async def c_start(message: Context):
    if store_to_processing(message):
        if blackjack.game_records.get(str(message.channel.id)):
            await message.channel.send("A game has started! Please wait for the next game.")
        else:
            embed = discord.Embed()
            embed.type = "rich"
            embed.set_author(name="A game is started! Use command \"!join\" to join this game. ")
            embed.set_footer(text=f"The game will start in {turn_count} second(s).")

            m = await message.channel.send(embed=embed)
            loop.create_task(blackjack.game_task(message.channel, m))
        delete_from_processing(message)
    else:
        await message.reply("Error! Please wait for the last command finish.")

@bot.command(name="bj_start", description="Start a BlackJack game", scope=guild_ids)
async def c__start(ctx: interactions.CommandContext):
    if store_to_processing("", ctx):
        channel = tools.get_channel_from_ctx(client, ctx)
        if blackjack.game_records.get(str(ctx.channel_id)):
            await ctx.send("A game has started! Please wait for the next game.")
        else:
            embed = discord.Embed()
            embed.type = "rich"
            embed.set_author(name="A game is started! Use command \"!join\" to join this game. ")
            embed.set_footer(text=f"The game will start in {turn_count} second(s).")

            m = await channel.send(embed=embed)
            loop.create_task(blackjack.game_task(channel, m))
        delete_from_processing("", ctx)
        await ctx.send("A game is staring...")
    else:
        await ctx.send("Error! Please wait for the last command finish.")

## bj!join
@client.command(name="join")
async def c_bj_join(message: Context):
    if store_to_processing(message):
        channel_id = str(message.channel.id)
        try:
            m_s = message.message.content.lower().split(" ")
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
            print("?")
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
                    await blackjack.step(game_records[channel_id])
            else:
                await message.channel.send("The max limit for a game is 6 players. Please wait for the next game.")
        else:
            await message.reply(f"Use command bj!start to create a game first.")
        delete_from_processing(message)
    else:
        await message.reply("Error! Please wait for the last command finish.")

@bot.command(name="bj_join", description="Join a BlackJack game", scope=guild_ids, 
    options=[interactions.Option(name="chips", description="How many chips do you want to bet?", required=True, type=interactions.OptionType.INTEGER, min_value=100)])
async def c__bj_join(ctx: interactions.CommandContext, chips: int):
    if store_to_processing("", ctx):
        channel = tools.get_channel_from_ctx(client, ctx)
        channel_id = str(channel.id)
        
        if game_records.get(channel_id):
            if game_records[channel_id]["step"] != 0:
                await ctx.send(f"A game is started. Please wait for the next game.")
                delete_from_processing("", ctx)
                return
            if len(game_records[channel_id]["players"]) < 6:
                db = DB()
                success, balance = db.bet(ctx.author.user.id, chips)
                if success:
                    await ctx.send(f"You joined the game, now you left {balance} Nicoins.")
                else:
                    await ctx.send(f"You don't have enough Nicoins to bet. Your Nicoins: {balance}")
                    db.close()
                    delete_from_processing("", ctx)
                    return
                db.close()
                game_records[channel_id]["players"].append({"user_id": int(ctx.author.user.id), "user_name": get_ctx_display_name(ctx), "bet_amount": chips, "stand": False, "cards": [], "result": None})

                if async_delay > 2:
                    await blackjack.step(game_records[channel_id])
            else:
                await ctx.send("The max limit for a game is 6 players. Please wait for the next game.")
        else:
            await ctx.send(f"Use command `/bj_start` to create a game first.")

        delete_from_processing("", ctx)
    else:
        await ctx.send("Error! Please wait for the last command finish.")

## hit
@client.command(name="hit")
async def c_hit(message: Context):
    if store_to_processing(message):
        if blackjack.game_records.get(str(message.channel.id)):
            channel_id = str(message.channel.id)
            if game_records.get(channel_id):
                turn = game_records[channel_id]["turn"]
                if game_records[channel_id]["step"] != 2 or game_records[channel_id]["players"][turn]["user_id"] != message.author.id:
                    await message.reply(f"Not your turn.")
                    delete_from_processing(message)
                    return
                else:
                    cards, points = blackjack.show_cards(game_records[channel_id]["players"][turn]["cards"])
                    if (len(game_records[channel_id]['players'][turn]["cards"]) < 5 or points < 21) and not game_records[channel_id]['players'][turn]["stand"]:
                        game_records[channel_id]['players'][turn]["cards"].append(blackjack.hit_a_card(game_records[channel_id]['cards']))
                        game_records[channel_id]['hit'] = True
                    else:
                        await message.reply("Invalid command.")
            else:
                await message.reply(f"Use command bj!start to create a game first.")
        delete_from_processing(message)
    else:
        await message.reply("Error! Please wait for the last command finish.")

@bot.command(name="bj_hit", description="Hit a card", scope=guild_ids)
async def c__hit(ctx: interactions.CommandContext):
    if store_to_processing("", ctx):
        channel = tools.get_channel_from_ctx(client, ctx)
        channel_id = str(channel.id)
        if blackjack.game_records.get(str(channel_id)):
            if game_records.get(channel_id):
                turn = game_records[channel_id]["turn"]
                if game_records[channel_id]["step"] != 2 or game_records[channel_id]["players"][turn]["user_id"] != int(ctx.author.user.id):
                    await ctx.send(f"Not your turn.")
                    delete_from_processing("", ctx)
                    return
                else:
                    cards, points = blackjack.show_cards(game_records[channel_id]["players"][turn]["cards"])
                    if (len(game_records[channel_id]['players'][turn]["cards"]) < 5 or points < 21) and not game_records[channel_id]['players'][turn]["stand"]:
                        game_records[channel_id]['players'][turn]["cards"].append(blackjack.hit_a_card(game_records[channel_id]['cards']))
                        game_records[channel_id]['hit'] = True
                    else:
                        await ctx.send("Invalid command.")
            else:
                await ctx.send(f"Use command `bj_start` to create a game first.")
        delete_from_processing("", ctx)
        m = await ctx.send("success", ephemeral=True)
        await asyncio.sleep(0.5)
        m.delete()
    else:
        await ctx.send("Error! Please wait for the last command finish.")

loop = asyncio.get_event_loop()
# task2 = loop.create_task(client.start(token, bot=True))
task2 = loop.create_task(client.start(token))
task1 = loop.create_task(bot.start())

gathered = asyncio.gather(task1, task2, loop=loop)
loop.run_until_complete(gathered)

# bot.start()