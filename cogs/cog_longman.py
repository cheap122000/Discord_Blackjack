import discord
from discord.ext import commands
from discord.ext.commands.context import Context
from discord.commands.context import ApplicationContext
from functions.tools import *
from functions import profile, tools, db_game
from typing import Optional, Union, Tuple
from games import longman
import time

class LongMan(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(name="lm_start")
    async def c_lm_start(self, ctx: Context):
        await start(ctx)

    @commands.command(name="lm_join")
    async def c_lm_join(self, ctx: Context):
        await join(ctx)

    @commands.slash_command(name="lm_start", description="在這個伺服器開始一場射龍門遊戲", guild_ids=guild_ids)
    async def s_lm_start(self, ctx: ApplicationContext):
        await start(ctx)

    @commands.slash_command(name="lm_join", description="使用 100 個 Nicoin 來加入一場射龍門遊戲", guild_ids=guild_ids)
    async def s_lm_join(self, ctx: Context):
        await join(ctx)

async def start(ctx: Optional[Union[Context, ApplicationContext]]):
    if store_to_processing(ctx):
        if longman.game_records.get(str(ctx.guild.id)):
            if longman[str(ctx.guild.id)]["start_time"] - time.time() < 60:
                await send_message(ctx, "一個伺服器同時只能有一場射龍門遊戲，請等待上一場遊戲結束")
                delete_from_processing(ctx)
                return

        embed = discord.Embed()
        embed.type = "rich"
        embed.set_author(name="遊戲開始! 使用指令 `bj!lm_join` 或 `/lm_join` 自動支付 100 Nicoin 加入這場遊戲")
        embed.set_footer(text=f"遊戲將在 {longman.turn_count} 秒後開始，還有 {longman.seats} 個座位")

        await send_message(ctx, "OK", ephemeral=True)
        m = await create_message(ctx, embed=embed)
        loop.create_task(longman.game_task(ctx.channel, str(ctx.guild.id), m))
        delete_from_processing(ctx)
    else:
        await reply_message(ctx, "錯誤！請等待前一個指令執行完畢")

async def join(ctx: Optional[Union[Context, ApplicationContext]]):
    if store_to_processing(ctx):
        # channel_id = str(ctx.channel.id)
        guild_id = str(ctx.guild.id)

        if longman.game_records.get(guild_id):
            if longman.game_records[guild_id]["step"] != 0:
                await reply_message(ctx, f"有一場射龍門遊戲已經開始了，請等待下一場")
                delete_from_processing(ctx)
                return
                
            if len(longman.game_records[guild_id]["players"]) < 10:
                db = DB()
                success, balance, prize = db.bet_to_pool(ctx.author.id, ctx.guild.id, 100)
                if success:
                    longman.game_records[guild_id]["prize"] = prize
                    delete_from_processing(ctx)
                    await reply_message(ctx, f"你加入了一場射龍門，剩餘 {balance} :coin:")
                    db.close()
                    longman.game_records[guild_id]["players"].append({"user_id": ctx.author.id, "user_name": ctx.author.display_name, "bet_amount": 0, "bet": "", "cards": [], "revealed": False, "result": None})
                    return
                else:
                    await reply_message(ctx, f"你至少必須有 100 :coin: 當作入場費加入射龍門. 你的餘額： {balance} :coin:")
                    db.close()
                    delete_from_processing(ctx)
                    return
            else:
                await reply_message(ctx, "一場 射龍門 最多只能 10 個人遊玩，請等待下一場遊戲開始")
        else:
            await reply_message(ctx, f"請先使用指令 `bj!lm_start` 或 `/lm_start` 創立一場 射龍門 遊戲")
        delete_from_processing(ctx)
    else:
        await reply_message(ctx, "錯誤！請等待前一個指令執行完畢")