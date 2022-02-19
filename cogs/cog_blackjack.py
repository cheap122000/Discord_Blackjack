import discord
from discord.ext import commands
from discord.ext.commands.context import Context
from discord.commands import slash_command, Option
from discord.commands.context import ApplicationContext
from functions.tools import *
from games import blackjack

class c_bj(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(name="start")
    async def start(self, ctx: Context):
        await start(ctx)

    @commands.command(name="join")
    async def join(self, ctx: Context):
        try:
            m_s = ctx.message.content.lower().split(" ")
            if len(m_s) != 2:
                await ctx.send("bj!join needs 1 parameter.")
                return
            bet_amount = int(m_s[1])
            if bet_amount < 100:
                await ctx.send("Your bet amount must be at least 100 Nicoins.")
                return
        except:
            await ctx.send("Your bet amount must be at least 100 Nicoins.")
            return
        await join(ctx, bet_amount)

class s_bj(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @slash_command(name="bj_start", description="Start a BlackJack game", guild_ids=guild_ids)
    async def start(self, ctx: ApplicationContext):
        await start(ctx)

    @slash_command(name="bj_join", description="Join a BlackJack game", guild_ids=guild_ids)
    async def join(self, ctx: ApplicationContext, chips: Option(int, "How many chips you want to bet?", min_value=100)):
        await join(ctx, chips)

async def start(ctx: Optional[Union[Context, ApplicationContext]]):
    if store_to_processing(ctx):
        if blackjack.game_records.get(str(ctx.channel.id)):
            await send_message(ctx, "A game has started! Please wait for the next game.")
        else:
            embed = discord.Embed()
            embed.type = "rich"
            embed.set_author(name="A game is started! Use command \"!join\" to join this game. ")
            embed.set_footer(text=f"The game will start in {blackjack.turn_count} second(s).")

            await send_message(ctx, "OK", ephemeral=True)
            m = await create_message(ctx, embed=embed)
            loop.create_task(blackjack.game_task(ctx.channel, m))
        delete_from_processing(ctx)
    else:
        await reply_message(ctx, "Error! Please wait for the last command finish.")
    

async def join(ctx: Optional[Union[Context, ApplicationContext]], bet_amount):
    if store_to_processing(ctx):
        channel_id = str(ctx.channel.id)

        if blackjack.game_records.get(channel_id):
            if blackjack.game_records[channel_id]["step"] != 0:
                await reply_message(ctx, f"A game is started. Please wait for the next game.")
                delete_from_processing(ctx)
                return
                
            if len(blackjack.game_records[channel_id]["players"]) < 6:
                db = DB()
                success, balance = db.bet(ctx.author.id, bet_amount)
                if success:
                    await reply_message(ctx, f"You joined the game, now you left {balance} Nicoins.")
                else:
                    await reply_message(ctx, f"You don't have enough Nicoins to bet. Your Nicoins: {balance}")
                    db.close()
                    delete_from_processing(ctx)
                    return
                db.close()
                blackjack.game_records[channel_id]["players"].append({"user_id": ctx.author.id, "user_name": ctx.author.display_name, "bet_amount": bet_amount, "stand": False, "cards": [], "result": None})
            else:
                await reply_message(ctx, "The max limit for a game is 6 players. Please wait for the next game.")
        else:
            await reply_message(ctx, f"Use command `bj!start` to create a game first.")
        delete_from_processing(ctx)
    else:
        await reply_message(ctx, "Error! Please wait for the last command finish.")