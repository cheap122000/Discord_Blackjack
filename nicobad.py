import discord
from discord.ext import commands
from discord.ext.commands.context import Context
from discord.ext.commands import Bot

token = "OTkxMDAyNDA1Mjk2NTcwNDI4.G6TamT.PirkkwWuAPORya03Uwks1NvzI0-7x0_Lc-UE18"

bot = Bot(intents=discord.Intents.all())

@bot.event
async def on_message_delete(msg: discord.Message):
    await msg.channel.send(f"<@{msg.author.id}> 壞壞，剛剛偷偷刪了一則訊息，內容是：\n{msg.content}")

@bot.event
async def on_message_edit(msg_before: discord.Message, msg_after: discord.Message):
    await msg_before.reply(f"<@{msg_before.author.id}> 不乖，剛剛偷偷修改了一則訊息，原始內容是：\n{msg_before.content}")

@bot.event
async def on_ready():
    print(f"bot is ready, login as {bot.user}")

bot.run(token)