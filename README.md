## Rarity Bot

This bot will can do advanture for all of your `Rarity Summonners` as soon as possible and level up them automaticlly.

#### USE IT AT YOUR OWN RISK.

### Installation

1. Clone this repo and go inside directory:

```
git clone https://github.com/iRhonin/rarity-bot.git
cd rarity-bot/
```

2. Install dependencies using Poetry or Pip:

    Poetry:
    `poetry install`

    Pip (in a virtualenv):
    `pip install requirements.txt`

3. Make a copy on `.env_example` and fill your `PRIVATE_KEY` and `ADDRESS` (`PRIVATE_KEY` is only needed to sign transactions, you can export it from the metamask):

    - `cp .env_example .env`
    - Set `PRIVATE_KEY` and `ADDRESS` (DO NOT SHARE YOUR PRIVATE KEY WITH ANYONE)
    - (Optional) Change other variables if needed

### Usage

To run with all of your summoners:

`python rarity/adventure.py`

Or with selected ones (If your summoners are 1234 and 4321):

`python rarity/adventure.py --summoners 1234 --summoners 4321`

---

If you want to disable automatic level-up, use `--no-lvlup`.

---
 
To see all options:

`python rarity/adventure.py --help`

---

If you had any issue, [issue tab](https://github.com/iRhonin/rarity-bot/issues) is for you, or you can find contacts on my profile.
