import discord
from discord.ext import commands
from discord.ext.commands.context import Context
from discord.commands import slash_command, Option
from discord.commands.context import ApplicationContext
from functions.tools import *
from games import blackjack

class BJGame(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(name="start")
    async def c_start(self, ctx: Context):
        await start(ctx)

    @commands.command(name="join")
    async def c_join(self, ctx: Context):
        try:
            m_s = ctx.message.content.lower().split(" ")
            if len(m_s) != 2:
                await ctx.send("bj!join 需要填入一個參數(籌碼)")
                return
            bet_amount = int(m_s[1])
            if bet_amount < 100:
                await ctx.send("你至少得下注 100 :coin:")
                return
        except:
            await ctx.send("你至少得下注 100 :coin:")
            return
        await join(ctx, bet_amount)

    @slash_command(name="bj_start", description="在頻道內開始一場21點遊戲", guild_ids=guild_ids)
    async def s_start(self, ctx: ApplicationContext):
        await start(ctx)

    @slash_command(name="bj_join", description="加入一場在頻道內的21點遊戲", guild_ids=guild_ids)
    async def s_join(self, ctx: ApplicationContext, chips: Option(int, "你要下注多少籌碼呢？", min_value=100)):
        await join(ctx, chips)

async def start(ctx: Optional[Union[Context, ApplicationContext]]):
    if store_to_processing(ctx):
        if blackjack.game_records.get(str(ctx.channel.id)):
            if blackjack.game_records[str(ctx.channel.id)]["start_time"] - time.time() < 60:
                await send_message(ctx, "頻道內已經開始了一場遊戲，請等待下一場遊戲")
                delete_from_processing(ctx)
                return

        embed = discord.Embed()
        embed.type = "rich"
        embed.set_author(name="頻道內已經開始了一場遊戲，請等待下一場遊戲")
        embed.set_footer(text=f"遊戲將在 {blackjack.turn_count} 秒後開始")

        await send_message(ctx, "OK", ephemeral=True)
        m = await create_message(ctx, embed=embed)
        loop.create_task(blackjack.game_task(ctx.channel, m))
        delete_from_processing(ctx)
    else:
        await reply_message(ctx, "錯誤！請等待前一個指令執行完畢")
    

async def join(ctx: Optional[Union[Context, ApplicationContext]], bet_amount):
    if store_to_processing(ctx):
        channel_id = str(ctx.channel.id)

        if blackjack.game_records.get(channel_id):
            if blackjack.game_records[channel_id]["step"] != 0:
                await reply_message(ctx, f"頻道內已經開始了一場遊戲，請等待下一場遊戲")
                delete_from_processing(ctx)
                return
                
            if len(blackjack.game_records[channel_id]["players"]) < 6:
                db = DB()
                success, balance = db.bet(ctx.author.id, bet_amount)
                if success:
                    await reply_message(ctx, f"你加入了一場遊戲，你剩下 {balance} :coin:")
                else:
                    await reply_message(ctx, f"你的籌碼不夠囉！ 你的籌碼: {balance} :coin:")
                    db.close()
                    delete_from_processing(ctx)
                    return
                db.close()
                blackjack.game_records[channel_id]["players"].append({"user_id": ctx.author.id, "user_name": ctx.author.display_name, "bet_amount": bet_amount, "stand": False, "cards": [], "result": None})
            else:
                await reply_message(ctx, "一場 21點 最多只能 6 個人遊玩，請等待下一場遊戲開始")
        else:
            await reply_message(ctx, f"請先使用指令 `bj!start` 或 `/bj_start` 創立一場 21點 遊戲")
        delete_from_processing(ctx)
    else:
        await reply_message(ctx, "錯誤！請等待前一個指令執行完畢")