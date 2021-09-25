## Rarity Bot

This bot will can do advanture for all of your `Rarity Summonners` as soon as possible and level up them automaticlly.

#### USE IT AT YOUR OWN RISK.

##### Under developmnet, please keep your clone/fork updated.

### Requirements

- Python 3.8+
- [Poetry 1.1+](https://python-poetry.org/docs/#installation)

### Installation

1. Clone this repo and cd into `rarity-bot` directory:

   ```
   git clone https://github.com/iRhonin/rarity-bot.git
   cd rarity-bot/
   ```

2. Install dependencies using Poetry:

   ```bash
   poetry install
   poetry shell  # Enter into virtualenv
   ```

   Note: If you ran into `fatal error: Python.h: No such file or directory` error, you need to install `python3-dev` on Ubuntu (`sudo apt install python3-dev`). Check [this](https://stackoverflow.com/a/21530768/9624798) link for the other distributions.

3. Make a copy on `.env_example` and fill your `PRIVATE_KEY` and `ADDRESS` (`PRIVATE_KEY` is only needed to sign transactions, you can export it from the metamask):

   - `cp .env_example .env`
   - Set `PRIVATE_KEY` and `ADDRESS` (DO NOT SHARE YOUR PRIVATE KEY WITH ANYONE)
   - (Optional) Change other variables if needed

### Usage

To send all of your summoners to advanture:

```
rarity adventure
```

Or only selected ones (If your summoners are 1234 and 4321):

```
rarity --summoner 1234 --summoner 4321 adventure
```

---

If you want to disable automatic level-up, use `--no-lvlup` like this:

```
rarity adventure --no-lvlup
```

---

To see all options:

```
rarity --help
```

---

If you had any issue, [issue tab](https://github.com/iRhonin/rarity-bot/issues) is for you, or you can find contacts on my profile.
