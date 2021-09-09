## Rarity Bot

This bot will can do advanture for all of your `Rarity Summonners` as soon as possible and level up them automaticlly.

#### USE IT AT YOUR OWN RISK.

### Installation

1. Clone this repo and go inside directory:

```
    xxx
```

2. Install dependencies using Poetry or Pip:

Poetry:
`poetry install`

Pip:
`pip install requirements.txt`

3. Make a copy on `.env_example` and fill your `PRIVATE_KEY` and `ADDRESS` (`PRIVATE_KEY` is only needed to sign transactions):

    - `cp .env_example .env`
    - Fill `PRIVATE_KEY` and `ADDRESS`
    - (Optional) Change other variables if needed

### Usage

To run with all of your summoners:

`python adventure.py`

Or with selected ones (If your summoners are 1234 and 4321):

`python adventure.py --summoners 1234 --summoners 4321`

---

If you want to disable automatic level-up, use `--no-lvlup`.
