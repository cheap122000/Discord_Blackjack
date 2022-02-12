from dis import dis
from unicodedata import name
import discord

class helpCenter():
    def __init__(self):
        self.help = self.help_center
    
    def help_center(self):
        embed = discord.Embed()
        embed.set_author(name="")

        return embed