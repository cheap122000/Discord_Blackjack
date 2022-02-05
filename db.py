import sqlite3

class DB:
    def __init__(self):
        self.conn = sqlite3.connect("./card.db3", check_same_thread=False)
        self.c = self.conn.cursor()

    def query_data(self, instruction):
        rows = self.c.execute(instruction).fetchall()
        return rows

    def operate_db(self, instruction):
        count = self.c.execute(instruction)
        self.conn.commit()
        return count
    
    def close(self):
        self.conn.close()
