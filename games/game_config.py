deck_of_card = {}
for i in range(52):
    temp = {}
    temp["r_number"] = i % 13
    temp["point"] = 10 if temp["r_number"] > 8 else 11 if temp["r_number"] == 0 else temp["r_number"] + 1
    temp["number"] = "A" if temp["r_number"] == 0 else "J" if temp["r_number"] == 10 else "Q" if temp["r_number"] == 11 else "K" if temp["r_number"] == 12 else str(temp["r_number"] + 1)
    temp["suit"] = "spades" if i < 13 else "hearts" if i < 26 else "diamonds" if i < 39 else "clubs"
    deck_of_card[i] = temp

new_deck = [i for i in range(52)]

async_delay = 1