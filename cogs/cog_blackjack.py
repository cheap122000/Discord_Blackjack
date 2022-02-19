import discord
from discord.ext import commands
from discord.ext.commands.context import Context
from discord.commands import slash_command
from discord.commands.context import ApplicationContext
from functions.tools import guild_ids

class c_blackjack(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

class s_blackjack(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot