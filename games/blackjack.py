from .game_config import *
import asyncio
import time

game_records = {}

async def game_task(channel, m):
    # db = DB()
    return
    channel_id = str(channel.id)
    if channel_id in game_records:
        await channel.send("A game has started! Please wait for the next game.")
        return
    game_records[channel_id] = {"players": [], "turn": -1, "hit":False, "dealer": {"cards": []}, "message": m, "start_time": int(time.time()), "step": 0, "record": {}, "cards": [i for i in range(52)]}

    while True:
        if game_records[channel_id]["step"] == 0:
            await step(game_records[channel_id])
        elif game_records[channel_id]["step"] == 1:
            game_records[channel_id]["dealer"]["cards"].append(hit_a_card(game_records[channel_id]["cards"]))
            await step1(game_records[channel_id])
        elif game_records[channel_id]["step"] == 2:
            await step2(game_records[channel_id])
        elif game_records[channel_id]["step"] == 3:
            await step3(game_records[channel_id])
        elif game_records[channel_id]["step"] == 4:
            await step4(game_records[channel_id])


        if game_records[channel_id]["step"] == 5:
            game_records.pop(channel_id)
            break
        # db.save_game(channel_id, game_records[channel_id])
        # print(game_records[channel_id]["step"])
        await asyncio.sleep(async_delay)