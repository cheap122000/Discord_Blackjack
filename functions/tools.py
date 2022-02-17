from .db_game import DB
from discord.ext.commands import Bot
import interactions

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
    ret = [int(row[0]) for row in rows]
    db.close()
    return ret

def get_channel_from_ctx(client: Bot, ctx: interactions.CommandContext):
    return client.get_channel(id=int(ctx.channel_id))