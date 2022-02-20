# Discord_BlackJack

## First setup
- Create two new files named "token.txt" and "token_dev.txt".
- Paste your discord bot's token in "token.txt".
- Paste your development discord bot's token in "token_dev.txt".

- Create another file name "token_setting.json"
- `{"dev": true, "guild_ids": [your_dev_dicord_guild_id]}`
    - if "dev" is true, "guild_ids" will pass to your slash command, token will be "token_dev.txt"
    - else, slash command's guild_ids will be None, token will be "token.txt"

## Casino bot
```
$ python casino.py
```