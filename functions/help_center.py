import discord
from discord.commands.context import ApplicationContext
from discord.ext.commands.context import Context

class helpCenter():
    def __init__(self):
        self.help = self.help_center()
        self.help_command = self.help_template()

    
    def help_center(self) -> discord.Embed():
        embed = discord.Embed()
        embed.colour = discord.Colour.purple()
        embed.set_author(name="NicoJack Help Center", icon_url="https://i.imgur.com/YFo8xQ1.jpg")
        embed.add_field(name=":coin: Infos", value="`bj!p`, `bj!pool`,\n`bj!daily`", inline=True)
        embed.add_field(name=":coin: BlackJack", value="`bj!start`, `bj!join`,\n`bj!hit`, `bj!double`, `bj!stand`", inline=True)
        embed.add_field(name=":coin: Gamble", value="`bj!gamble`", inline=True)
        embed.add_field(name=":coin: LongMan", value="`bj!lm_start`, `bj!lm_join`", inline=True)

        return embed

    def help_template(self) -> discord.Embed():
        embed = discord.Embed()
        embed.colour = discord.Colour.purple()
        embed.set_author(name="NicoJack Help Center", icon_url="https://i.imgur.com/YFo8xQ1.jpg")
        embed.add_field(name="", value="", inline=False)
        embed.add_field(name="", value="", inline=False)
        embed.add_field(name="", value="", inline=False)

        return embed

    def set_help_center(self, message:Context, ctx:ApplicationContext=None):
        if ctx:
            embed = discord.Embed()
            embed.colour = discord.Colour.purple()
            embed.set_author(name="NicoJack Help Center", icon_url="https://i.imgur.com/YFo8xQ1.jpg")
            embed.set_footer(text=f"{ctx.author.display_name}#{ctx.author.discriminator}. Use slash commands to play games eaily.", icon_url=ctx.author.display_avatar)
            embed.add_field(name=":coin: Infos", value="`profile`, `pool`\n`daily`, `leader_board`", inline=True)
            embed.add_field(name=":coin: Balance", value="`give`", inline=True)
            embed.add_field(name=":coin: Gamble", value="`gamble`", inline=True)
            embed.add_field(name=":coin: BlackJack", value="`bj_start`, `bj_join`", inline=True)
            embed.add_field(name=":coin: LongMan", value="`lm_start`, `lm_join`", inline=True)

            return embed
        else:
            commands = message.message.content.lower().split(" ")
            if len(commands) == 1:
                self.help.set_footer(text=f"{message.author.display_name}#{message.author.discriminator}. Use bj!help <command> for more detailed instructions.", icon_url=message.author.display_avatar)
                return self.help
            elif len(commands) == 2:
                if commands[1] in ["p", "bj!p"]:
                    self.help_command.set_field_at(0, name="`bj!p`", value="See how many :coin:(Nicoins) you have.", inline=False)
                    self.help_command.set_field_at(1, name="Category", value="Information", inline=False)
                    self.help_command.set_field_at(2, name="Method", value="`bj!p`", inline=False)
                elif commands[1] in ["daily", "bj!daily"]:
                    self.help_command.set_field_at(0, name="`bj!daily`", value="Obtain daily 1000 :coin:", inline=False)
                    self.help_command.set_field_at(1, name="Category", value="Information", inline=False)
                    self.help_command.set_field_at(2, name="Method", value="`bj!daily`", inline=False)
                elif commands[1] in ["gamble", "bj!gamble"]:
                    self.help_command.set_field_at(0, name="`bj!gamble`", value="Random a number between 1 and 100.\n1~60: Lose your :coin:.\n61~97: Win the :coin: you bet.\n98~100: Win 2x :coin: you bet.", inline=False)
                    self.help_command.set_field_at(1, name="Category", value="Gamble", inline=False)
                    self.help_command.set_field_at(2, name="Method", value="`bj!gamble <Nicoins>`\nYou must bet **at least 1 Nicoin**.", inline=False)
                elif commands[1] in ["start", "bj!start"]:
                    msg = "Create a BlackJack game in this channel. The game will start in 30 seconds.\n"
                    msg += "During this period, you can use `bj!join <Nicoins>` to join the game.\n"
                    msg += "After the game starting, Dealer will get 1 card, and each player will get 2 cards.\n"
                    msg += "**A** for 1 or 11 points, **J, Q, K** for 10 points, 2~10 for 2~10 points\n"
                    msg += "Use `bj!hit` to hit a card, `bj!double` to double your chips, `bj!stand` to stand.\n"
                    msg += "When players finish their rounds, Dealer will draw a card if his points are less than 17.\n"
                    msg += "**BlackJack**: You got a **A** and a 10-point card.\n"
                    msg += "**Five-card**: You got five cards and points less than or equal 21.\n"
                    msg += "**Twenty-one**: You got 21 points via 3-5 cards.\n"
                    msg += "**Busted**: You points greater than 21.\n"
                    msg += "Order: Black Jack > Five-card > Twenty-one > 0~20 > Busted"
                    self.help_command.set_field_at(0, name="`bj!start`", value=msg, inline=False)
                    self.help_command.set_field_at(1, name="Category", value="BlackJack", inline=False)
                    self.help_command.set_field_at(2, name="Method", value="`bj!start`", inline=False)
                elif commands[1] in ["join", "bj!join"]:
                    self.help_command.set_field_at(0, name="`bj!join`", value="Join the game in the channel.", inline=False)
                    self.help_command.set_field_at(1, name="Category", value="BlackJack", inline=False)
                    self.help_command.set_field_at(2, name="Method", value="`bj!join <Nicoins>`\nYou must bet **at least 100 Nicoins**.", inline=False)
                elif commands[1] in ["hit", "bj!hit"]:
                    self.help_command.set_field_at(0, name="`bj!hit`", value="Hit a card.", inline=False)
                    self.help_command.set_field_at(1, name="Category", value="BlackJack", inline=False)
                    self.help_command.set_field_at(2, name="Method", value="`bj!hit`", inline=False)
                elif commands[1] in ["double", "bj!double"]:
                    self.help_command.set_field_at(0, name="`bj!double`", value="Double your chips.", inline=False)
                    self.help_command.set_field_at(1, name="Category", value="BlackJack", inline=False)
                    self.help_command.set_field_at(2, name="Method", value="`bj!double`", inline=False)
                elif commands[1] in ["stand", "bj!stand"]:
                    self.help_command.set_field_at(0, name="`bj!stand`", value="Stand and turn to the next player", inline=False)
                    self.help_command.set_field_at(1, name="Category", value="BlackJack", inline=False)
                    self.help_command.set_field_at(2, name="Method", value="`bj!stand`", inline=False)
                elif commands[1] in ["lm_start", "bj!lm_start"]:
                    self.help_command.set_field_at(0, name="`bj!lm_start`", value="Start a LongMan game", inline=False)
                    self.help_command.set_field_at(1, name="Category", value="BlackJack", inline=False)
                    self.help_command.set_field_at(2, name="Method", value="`bj!lm_start`", inline=False)
                elif commands[1] in ["lm_join", "bj!lm_join"]:
                    self.help_command.set_field_at(0, name="`bj!lm_join`", value="Join a LongMan Game in the server.", inline=False)
                    self.help_command.set_field_at(1, name="Category", value="BlackJack", inline=False)
                    self.help_command.set_field_at(2, name="Method", value="`bj!lm_join`", inline=False)
                return self.help_command