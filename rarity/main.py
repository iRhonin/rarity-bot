from typing import List

import typer
from dotenv import load_dotenv

from rarity.constants import EXPLORER
from rarity.constants import EXPLORER_APIKEY
from rarity.constants import MAX_RETRIES
from rarity.constants import RARITY_ADRRESS
from rarity.constants import SLEEP_BEFORE_CONTINUE
from rarity.constants import UPDATE_EVERY_SECONDS
from rarity.constants import WEB3_RPC
from rarity.rarity import Rarity


load_dotenv()
app = typer.Typer()
rarity: Rarity = None


@app.callback()
def main(
    address: str = typer.Option(None, envvar='ADDRESS'),
    private_key: str = typer.Option(None, envvar='PRIVATE_KEY'),
    rarity_address: str = typer.Option(RARITY_ADRRESS, envvar='RARITY_ADRRESS'),
    summoners: List[int] = typer.Option(None, envvar='SUMMONERS'),
    web3_rpc: str = typer.Option(WEB3_RPC, envvar='WEB3_RPC'),
    max_retries: str = typer.Option(MAX_RETRIES, envvar='MAX_RETRIES'),
    update_every_seconds: str = typer.Option(
        UPDATE_EVERY_SECONDS, envvar='UPDATE_EVERY_SECONDS'
    ),
    sleep_before_continue: str = typer.Option(
        SLEEP_BEFORE_CONTINUE, envvar='SLEEP_BEFORE_CONTINUE'
    ),
    explorer: str = typer.Option(EXPLORER, envvar='EXPLORER'),
    explorer_apikey: str = typer.Option(EXPLORER_APIKEY, envvar='EXPLORER_APIKEY'),
):
    global rarity
    rarity = Rarity(
        web3_rpc=web3_rpc,
        private_key=private_key,
        address=address,
        rarity_address=rarity_address,
        summoners=summoners,
        max_retries=max_retries,
        update_every_seconds=update_every_seconds,
        sleep_before_continue=sleep_before_continue,
        explorer=explorer,
        explorer_apikey=explorer_apikey,
    )


@app.command()
def adventure(lvlup: bool = typer.Option(True, envvar='LVLUP')):
    rarity.send_all_to_adventure(lvl_up=lvlup)
