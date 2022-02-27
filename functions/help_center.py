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
        embed.set_author(name="NicoJack 幫助中心", icon_url="https://i.imgur.com/YFo8xQ1.jpg")
        embed.add_field(name=":coin: 資訊", value="`bj!p`, `bj!pool`,\n`bj!daily`", inline=True)
        embed.add_field(name=":coin: 21點", value="`bj!start`, `bj!join`,\n`bj!hit`, `bj!double`, `bj!stand`", inline=True)
        embed.add_field(name=":coin: 試運氣", value="`bj!gamble`", inline=True)
        embed.add_field(name=":coin: 射龍門", value="`bj!lm_start`, `bj!lm_join`", inline=True)

        return embed

    def help_template(self) -> discord.Embed():
        embed = discord.Embed()
        embed.colour = discord.Colour.purple()
        embed.set_author(name="NicoJack 幫助中心", icon_url="https://i.imgur.com/YFo8xQ1.jpg")
        embed.add_field(name="", value="", inline=False)
        embed.add_field(name="", value="", inline=False)
        embed.add_field(name="", value="", inline=False)

        return embed

    def set_help_center(self, message:Context, ctx:ApplicationContext=None):
        if ctx:
            embed = discord.Embed()
            embed.colour = discord.Colour.purple()
            embed.set_author(name="NicoJack 幫助中心", icon_url="https://i.imgur.com/YFo8xQ1.jpg")
            embed.set_footer(text=f"{ctx.author.display_name}#{ctx.author.discriminator} 使用斜線指令更方便的遊玩遊戲", icon_url=ctx.author.display_avatar)
            embed.add_field(name=":coin: 資訊", value="`profile`, `pool`\n`daily`, `leader_board`", inline=True)
            embed.add_field(name=":coin: 籌碼", value="`give`", inline=True)
            embed.add_field(name=":coin: 試運氣", value="`gamble`", inline=True)
            embed.add_field(name=":coin: 21點", value="`bj_start`, `bj_join`", inline=True)
            embed.add_field(name=":coin: 射龍門", value="`lm_start`, `lm_join`", inline=True)

            return embed
        else:
            commands = message.message.content.lower().split(" ")
            if len(commands) == 1:
                self.help.set_footer(text=f"{message.author.display_name}#{message.author.discriminator} 使用 bj!help <指令> 查看詳細指令功能.", icon_url=message.author.display_avatar)
                return self.help
            elif len(commands) == 2:
                if commands[1] in ["p", "bj!p"]:
                    self.help_command.set_field_at(0, name="`bj!p`", value="查看你有多少 :coin:(Nicoins)", inline=False)
                    self.help_command.set_field_at(1, name="分類", value="資訊", inline=False)
                    self.help_command.set_field_at(2, name="方法", value="`bj!p`", inline=False)
                elif commands[1] in ["daily", "bj!daily"]:
                    self.help_command.set_field_at(0, name="`bj!daily`", value="獲得每日 1000 :coin:", inline=False)
                    self.help_command.set_field_at(1, name="分類", value="資訊", inline=False)
                    self.help_command.set_field_at(2, name="方法", value="`bj!daily`", inline=False)
                elif commands[1] in ["gamble", "bj!gamble"]:
                    self.help_command.set_field_at(0, name="`bj!gamble`", value="系統從 1~100 隨機產生一個數字\n1~60: 輸掉你下注的 :coin:.\n61~97: 贏得你下注的 :coin:\n98~100: 贏得兩倍你下注的 :coin:", inline=False)
                    self.help_command.set_field_at(1, name="分類", value="試運氣", inline=False)
                    self.help_command.set_field_at(2, name="方法", value="`bj!gamble <Nicoins數量>`\n你 **至少得下注一枚 :coin:**.", inline=False)
                elif commands[1] in ["start", "bj!start"]:
                    msg = "在頻道內開始一場21點遊戲，遊戲將在30秒後開始\n"
                    msg += "期間內你可以使用 `bj!join <Nicoins>` 指令來加入這場遊戲\n"
                    msg += "遊戲開始後，莊家會拿到一張牌且其他玩家個會拿到兩張牌\n"
                    msg += "**A** 代表 1點 或是 11點 **J, Q, K** 代表 10點, 2~10 代表 2~10 點\n"
                    msg += "使用 `bj!hit` 要一張牌, `bj!double` 加倍你的賭注要一張牌後結束你的回合, `bj!stand` 停牌\n"
                    msg += "當所有使用者結束他們的回合後，莊家會開始補牌直到點數超過 17點\n"
                    msg += "牌型：\n"
                    msg += "**BlackJack**: 你的手牌只有 **A** 和一張 **10點** 的牌\n"
                    msg += "**過五關**: 要到五張手牌且點數總和不大於21點\n"
                    msg += "**21點**: 手牌點數總合為21點\n"
                    msg += "**爆牌**: 點數超過21點\n"
                    msg += "大小: BlackJack > 過五關 > 21點 > 0~20點 > 爆牌"
                    self.help_command.set_field_at(0, name="`bj!start`", value=msg, inline=False)
                    self.help_command.set_field_at(1, name="分類", value="21點", inline=False)
                    self.help_command.set_field_at(2, name="方法", value="`bj!start`", inline=False)
                elif commands[1] in ["join", "bj!join"]:
                    self.help_command.set_field_at(0, name="`bj!join`", value="加入一場頻道內的21點遊戲", inline=False)
                    self.help_command.set_field_at(1, name="分類", value="21點", inline=False)
                    self.help_command.set_field_at(2, name="方法", value="`bj!join <Nicoins>`\n你 **至少得下注100枚 :coin:**.", inline=False)
                elif commands[1] in ["hit", "bj!hit"]:
                    self.help_command.set_field_at(0, name="`bj!hit`", value="要一張牌", inline=False)
                    self.help_command.set_field_at(1, name="分類", value="21點", inline=False)
                    self.help_command.set_field_at(2, name="方法", value="`bj!hit`", inline=False)
                elif commands[1] in ["double", "bj!double"]:
                    self.help_command.set_field_at(0, name="`bj!double`", value="加倍下注", inline=False)
                    self.help_command.set_field_at(1, name="分類", value="21點", inline=False)
                    self.help_command.set_field_at(2, name="方法", value="`bj!double`", inline=False)
                elif commands[1] in ["stand", "bj!stand"]:
                    self.help_command.set_field_at(0, name="`bj!stand`", value="停牌並且換到下一位玩家", inline=False)
                    self.help_command.set_field_at(1, name="分類", value="21點", inline=False)
                    self.help_command.set_field_at(2, name="方法", value="`bj!stand`", inline=False)
                elif commands[1] in ["lm_start", "bj!lm_start"]:
                    self.help_command.set_field_at(0, name="`bj!lm_start`", value="開始一場射龍門遊戲", inline=False)
                    self.help_command.set_field_at(1, name="分類", value="射龍門", inline=False)
                    self.help_command.set_field_at(2, name="方法", value="`bj!lm_start`", inline=False)
                elif commands[1] in ["lm_join", "bj!lm_join"]:
                    self.help_command.set_field_at(0, name="`bj!lm_join`", value="加入一場在伺服器內的射龍門遊戲", inline=False)
                    self.help_command.set_field_at(1, name="分類", value="射龍門", inline=False)
                    self.help_command.set_field_at(2, name="方法", value="`bj!lm_join`", inline=False)
                return self.help_command