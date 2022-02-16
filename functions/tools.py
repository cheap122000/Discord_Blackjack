from .db_game import DB

def add_guild_to_db(guild_id):
    db = DB()
    rows = db.query_data(f"SELECT [guild_id] FROM [pools] WHERE [guild_id]='{guild_id}'")
    if len(rows):
        pass
    else:
        db.operate_db(f"INSERT INTO [pools] ([guild_id], [prize]) VALUES ('{guild_id}', '0')")

    db.close()

def get_guild_ids():
    db = DB()
    ret = []
    rows = db.query_data(f"SELECT [guild_id] FROM [pools]")
    ret = [row[0] for row in rows]
    db.close()
    return ret