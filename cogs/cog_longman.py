import discord
from discord.ext import commands
from discord.ext.commands.context import Context
from discord.commands.context import ApplicationContext
from functions.tools import *
from functions import profile, tools, db_game
from typing import Optional, Union, Tuple
from games import longman

class LongMan(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(name="lm_start")
    async def c_lm_start(self, ctx: Context):
        await start(ctx)

    @commands.command(name="lm_join")
    async def c_lm_join(self, ctx: Context):
        await join(ctx)

    @commands.slash_command(name="lm_start", description="Start a LongMan Game.", guild_ids=guild_ids)
    async def s_lm_start(self, ctx: ApplicationContext):
        await start(ctx)

    @commands.slash_command(name="lm_join", description="Join a LongMan Game with 100 Nicoins.", guild_ids=guild_ids)
    async def s_lm_join(self, ctx: Context):
        await join(ctx)

async def start(ctx: Optional[Union[Context, ApplicationContext]]):
    if store_to_processing(ctx):
        if longman.game_records.get(str(ctx.guild.id)):
            await send_message(ctx, "A server can only create a LongMan game in the same time, please wait for the last game has been finished.")
        else:
            embed = discord.Embed()
            embed.type = "rich"
            embed.set_author(name="A game is started! Use command `bj!lm_join` or `/lm_join` to join this game with 100 Nicoins.")
            embed.set_footer(text=f"The game will start in {longman.turn_count} second(s), {longman.seats} seats left.")

            await send_message(ctx, "OK", ephemeral=True)
            m = await create_message(ctx, embed=embed)
            loop.create_task(longman.game_task(ctx.channel, str(ctx.guild.id), m))
        delete_from_processing(ctx)
    else:
        await reply_message(ctx, "Error! Please wait for the last command finish.")

async def join(ctx: Optional[Union[Context, ApplicationContext]]):
    if store_to_processing(ctx):
        # channel_id = str(ctx.channel.id)
        guild_id = str(ctx.guild.id)

        if longman.game_records.get(guild_id):
            if longman.game_records[guild_id]["step"] != 0:
                await reply_message(ctx, f"A game is started. Please wait for the next game.")
                delete_from_processing(ctx)
                return
                
            if len(longman.game_records[guild_id]["players"]) < 10:
                db = DB()
                success, balance, prize = db.bet_to_pool(ctx.author.id, ctx.guild.id, 100)
                if success:
                    longman.game_records[guild_id]["prize"] = prize
                    await reply_message(ctx, f"You joined the game, now you left {balance} Nicoins.")
                else:
                    await reply_message(ctx, f"You should have at least 100 :coin: to join LongMan. Your Nicoins: {balance}")
                    db.close()
                    delete_from_processing(ctx)
                    return
                db.close()
                longman.game_records[guild_id]["players"].append({"user_id": ctx.author.id, "user_name": ctx.author.display_name, "bet_amount": 0, "bet": "", "cards": [], "revealed": False, "result": None})
            else:
                await reply_message(ctx, "The max limit for a game is 10 players. Please wait for the next game.")
        else:
            await reply_message(ctx, f"Use command `bj!lm_start` or `/lm_start` to create a game first.")
        delete_from_processing(ctx)
    else:
        await reply_message(ctx, "Error! Please wait for the last command finish.")