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

    def start_a_game(self, channel_id):
        rows = self.query_data(f"SELECT * FROM [games] WHERE [channel_id]='{channel_id}'")

        if len(rows) > 0:
            dealer, last_time = json.loads(rows[0][4]), int(rows[0][5])
            time_left = 60 - (int(time.time()) - last_time)
            time_left = 1 if time_left < 1 else time_left
            return dealer["step"], time_left
        else:
            self.operate_db(f"INSERT INTO [games] ([channel_id], [cards], [records], [dealer], [time]) VALUES ('{channel_id}', '[]', '{json.dumps(empty_dict)}', '{json.dumps(dealer_init)}', '{int(time.time())}')")
            return 0, 60
    
    def check_time(self):
        query_time = int(time.time()) - 60
        rows = self.query_data(f"SELECT [channel_id], [dealer] FROM [games] WHERE [time] < '{query_time}'")
        return [{"channel_id": row[0], "dealer": json.loads(row[1])} for row in rows]
    
    def close(self):
        self.conn.close()
