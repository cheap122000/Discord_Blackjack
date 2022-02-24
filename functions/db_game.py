import sqlite3
import json
import time
import datetime

# dealer step
# 0: wait for players
# 1: start game
dealer_init = {}
dealer_init["step"] = 0
empty_dict = {}

deck_of_card = {}
for i in range(52):
    temp = {}
    temp["number"] = i % 13
    temp["point"] = 10 if temp["number"] > 8 else 11 if temp["number"] == 0 else temp["number"] + 1
    temp["number"] = "A" if temp["number"] == 0 else "J" if temp["number"] == 10 else "Q" if temp["number"] == 11 else "K" if temp["number"] == 12 else str(temp["number"] + 1)
    temp["suit"] = "spades" if i < 13 else "hearts" if i < 26 else "diamonds" if i < 39 else "clubs"
    deck_of_card[i] = temp

new_deck = [i for i in range(52)]

class DB:
    def __init__(self):
        self.conn = sqlite3.connect("./db_bj.db3", check_same_thread=False)
        self.c = self.conn.cursor()

    def query_data(self, instruction):
        rows = self.c.execute(instruction).fetchall()
        return rows

    def operate_db(self, instruction):
        count = self.c.execute(instruction)
        self.conn.commit()
        return count

    def get_daily(self, dc_id):
        rows = self.query_data(f"SELECT * FROM [users] WHERE [dc_id]='{dc_id}'")

        if len(rows):
            balance = int(rows[0][2])
            daily_date = rows[0][3]
            if daily_date == int(datetime.datetime.now().strftime('%Y%m%d')):
                return False, balance
            else:
                self.operate_db(f"UPDATE [users] SET [currency]='{balance+1000}', [daily]='{datetime.datetime.now().strftime('%Y%m%d')}' WHERE [dc_id]='{dc_id}'")
                return True, balance+1000
        else:
            self.operate_db(f"INSERT INTO [users] ([dc_id], [currency], [daily]) VALUES ('{dc_id}', '1000', '{datetime.datetime.now().strftime('%Y%m%d')}')")
            return True, 1000
    
    def query_user_balance(self, dc_id):
        rows = self.query_data(f"SELECT * FROM [users] WHERE [dc_id]='{dc_id}'")

        if len(rows):
            balance = int(rows[0][2])
            return int(balance)
        else:
            return 0

    def bet(self, dc_id, bet_amount):
        rows = self.query_data(f"SELECT * FROM [users] WHERE [dc_id]='{dc_id}'")

        if len(rows):
            balance = int(rows[0][2])
            if bet_amount > int(balance):
                return False, balance
            else:
                balance -= bet_amount
                self.operate_db(f"UPDATE [users] SET [currency]='{balance}' WHERE [dc_id]='{dc_id}'")
                return True, balance
        else:
            return False, 0

    def bet_to_pool(self, dc_id, guild_id, bet_amount):
        rows = self.query_data(f"SELECT * FROM [users] WHERE [dc_id]='{dc_id}'")

        if len(rows):
            balance = int(rows[0][2])
            if bet_amount > int(balance):
                return False, balance
            else:
                balance -= bet_amount
                self.operate_db(f"UPDATE [users] SET [currency]='{balance}' WHERE [dc_id]='{dc_id}'")

                prize = self.query_guild_pool(guild_id) + bet_amount
                self.operate_db(f"UPDATE [pools] SET [prize]='{prize}' WHERE [guild_id]='{guild_id}'")
                return True, balance, prize
        else:
            return False, 0

    def get_balance(self, dc_id, bet_amount):
        rows = self.query_data(f"SELECT * FROM [users] WHERE [dc_id]='{dc_id}'")

        if len(rows):
            balance = int(rows[0][2])
            balance += bet_amount
            self.operate_db(f"UPDATE [users] SET [currency]='{balance}' WHERE [dc_id]='{dc_id}'")
            return balance
        else:
            self.operate_db(f"INSERT INTO [users] ([dc_id], [currency], [daily]) VALUES ('{dc_id}', '{bet_amount}', '0')")
            return bet_amount

    def query_guild_pool(self, guild_id):
        rows = self.query_data(f"SELECT * FROM [pools] WHERE [guild_id]='{guild_id}'")
        if len(rows):
            prize = int(rows[0][2])
            return prize
        else:
            self.operate_db(f"INSERT INTO [pools] ([guild_id], [prize]) VALUES ('{guild_id}', '0')")
            return 0

    def save_guild_pool(self, guild_id, prize):
        rows = self.query_data(f"SELECT * FROM [pools] WHERE [guild_id]='{guild_id}'")
        if len(rows):
            self.operate_db(f"UPDATE [pools] SET [prize]='{prize}' WHERE [guild_id]='{guild_id}'")
        else:
            self.operate_db(f"INSERT INTO [pools] ([guild_id], [prize]) VALUES ('{guild_id}', '0')")
    
    def check_time(self):
        query_time = int(time.time()) - 60
        rows = self.query_data(f"SELECT [channel_id], [dealer] FROM [games] WHERE [time] < '{query_time}'")
        return [{"channel_id": row[0], "dealer": json.loads(row[1])} for row in rows]
    
    def close(self):
        self.conn.close()
