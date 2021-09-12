from datetime import datetime
from multiprocessing.dummy import Pool as ThreadPool
from time import sleep
from typing import List

import typer
import web3
from dotenv import load_dotenv
from eth_utils import address
from web3 import Web3

from abis import RARITY_ABI
from utils import (fetch_erc721, format_timedelta, nonce, sign_and_send_txn,
                   tx_explorer_link)

RARITY_ADRRESS = "0xce761d788df608bd21bdd59d6f4b54b2e27f25bb"
WEB3_RPC = "https://rpc.ftm.tools/"
EXPLORER = "https://ftmscan.com/"
SLEEP_BEFORE_CONTINUE = 5
UPDATE_EVERY_SECONDS = 30 * 60
EXPLORER_APIKEY = "SF7K5UN374SAQ6H2YCFA8MQMRAN58DNFEM"
MAX_RETRIES = 10

COLORS = [
    '\033[95m',
    '\033[94m',
    '\033[92m',
    '\033[93m',
    '\033[0m',
]


class Rarity():
    def __init__(
        self, private_key, address, web3_rpc = WEB3_RPC, rarity_address = RARITY_ADRRESS, abi = RARITY_ABI, summoners = None,
        max_retries = MAX_RETRIES, update_every_seconds = UPDATE_EVERY_SECONDS, sleep_before_continue = SLEEP_BEFORE_CONTINUE,
        explorer = EXPLORER, explorer_apikey=EXPLORER_APIKEY
    ):
        self.web3_rpc = web3_rpc
        self.summoners_thread_list = []
        self.summoners = {}
        self.private_key = private_key
        self.address = Web3.toChecksumAddress(address)
        self.rarity_address = Web3.toChecksumAddress(rarity_address)
        self.abi = abi
        self.max_retries = max_retries
        self.update_every_seconds = update_every_seconds
        self.sleep_before_continue = sleep_before_continue
        self.explorer = explorer
        self.explorer_apikey = explorer_apikey
        self.remaining_times = {}

        if summoners:
            self.summoner_ids = summoners
        else:
            self.fetch_summoners()

    def fetch_summoners(self):
        print('Fetching summoners...')
        erc721s = fetch_erc721(self.explorer_apikey, self.address)
        if erc721s is None:
            print('No summoners found!')
            return

        self.summoner_ids = [
            int(s['tokenID']) for s in erc721s
            if address.is_same_address(s['contractAddress'], self.rarity_address)
        ]
        print('Found these summoners in the jungle: ', ' '.join([s for s in map(str, self.summoner_ids)]))

    def send_all_to_adventure(self, lvl_up=False):
        self.thread_pool = ThreadPool(len(self.summoner_ids))

        for summoner_id in self.summoner_ids:
            summoner = Summoner(
                web3_rpc=self.web3_rpc,
                private_key=self.private_key,
                address=self.address,
                rarity_address=self.rarity_address,
                abi=self.abi,
                summoner_id=summoner_id,
            )
            self.summoners[summoner.summoner_id] = summoner

        while True:
            for summoner in self.summoners.values():
                self.remaining_times[summoner.summoner_id] = summoner.adventure(lvl_up)

            sleep(min([*self.remaining_times.values(), UPDATE_EVERY_SECONDS]))


class Summoner():
    def __init__(
        self, private_key, address, rarity_address, abi, summoner_id, web3_rpc=WEB3_RPC,
        max_retries = MAX_RETRIES, update_every_seconds = UPDATE_EVERY_SECONDS, sleep_before_continue = SLEEP_BEFORE_CONTINUE,
        explorer = EXPLORER,
    ):
        self.web3 =  Web3(Web3.HTTPProvider(web3_rpc))
        self.private_key = private_key
        self.address = Web3.toChecksumAddress(address)
        self.rarity_address = Web3.toChecksumAddress(rarity_address)
        self.contract = self.web3.eth.contract(address=self.rarity_address, abi=abi)
        self.summoner_id=summoner_id
        self.max_retries = max_retries
        self.update_every_seconds = update_every_seconds
        self.sleep_before_continue = sleep_before_continue
        self.explorer = explorer

    def log(self, msg):
        color = COLORS[self.summoner_id % len(COLORS)]
        print(f'{color}Summoner #{self.summoner_id}: {msg}')

    def next_adventure_in(self):
        return self.contract.functions.adventurers_log(self.summoner_id).call()

    def remaining_time(self):
        next_adventure = self.next_adventure_in()
        timedelta = datetime.fromtimestamp(next_adventure) - datetime.now()
        return timedelta.total_seconds()

    def data(self):
        result = self.contract.functions.summoner(self.summoner_id).call()
        data = dict(
            xp=result[0],
            log=result[1],
            class_=result[2],
            level=result[3],
        )
        self.log(f'XP: {data.get("xp")}, Level: {data.get("level")}')
        return data

    def do_adventure(self):
        try:
            adventure_txn = self.contract.functions.adventure(self.summoner_id).buildTransaction(
                {"nonce": nonce(self.web3, self.address)}
            )
            tx_hash = sign_and_send_txn(self.web3, adventure_txn, self.private_key)
            self.log(f'Sending to adventure! {tx_explorer_link(self.explorer, tx_hash)}')
            return tx_hash
        except web3.exceptions.ContractLogicError:
            self.log('is sleeping!')

    def lvl_up(self):
        try:
            lvlup_txn = self.contract.functions.level_up(self.summoner_id).buildTransaction(
                {"nonce": nonce(self.web3, self.address)}
            )
            tx_hash = sign_and_send_txn(self.web3, lvlup_txn, self.private_key)
            self.log(f'Leveling UP! {tx_explorer_link(self.explorer, tx_hash)}')
            return tx_hash
        except web3.exceptions.ContractLogicError:
            return

    def adventure(self, lvl_up=False):
        while self.remaining_time() <= 0:
            tx_hash = None
            try:
                tx_hash = self.do_adventure()
            except Exception as ex:
                print(ex)
            finally:
                for _ in range(self.max_retries):
                    sleep(self.sleep_before_continue)
                    tx = self.web3.eth.getTransaction(tx_hash)
                    if tx and tx['blockNumber'] is not None:
                        self.log(f'did an adventure!')
                        self.data()
                        break
                else:
                    self.log(f'Adventure TX take too long to confirm! {tx_explorer_link(self.explorer, tx_hash)}')

        if lvl_up:
            lvlup_tx_hash = self.lvl_up()
            if lvlup_tx_hash is not None:
                for _ in range(self.max_retries):
                    sleep(self.sleep_before_continue)
                    lvlup_tx = self.web3.eth.getTransaction(lvlup_tx_hash)
                    if lvlup_tx and lvlup_tx['blockNumber'] is not None:
                        self.data()
                        break
                else:
                    self.log(f'Level-up TX take too long to confirm! {tx_explorer_link(self.explorer, lvlup_tx_hash)}')

        remaining_time = self.remaining_time()
        formated_remaining_time = format_timedelta(remaining_time)
        self.log(f'is sleeping for {formated_remaining_time[0]} Hours and {formated_remaining_time[1]} Minutes')
        return remaining_time


def adventure(
    address: str = typer.Option(None, envvar="ADDRESS"),
    private_key: str = typer.Option(None, envvar="PRIVATE_KEY"),
    rarity_address: str = typer.Option(RARITY_ADRRESS, envvar="RARITY_ADRRESS"),
    lvlup: bool = typer.Option(True, envvar="LVLUP"),
    summoners:  List[int] = typer.Option(None, envvar="SUMMONERS"),
    web3_rpc: str = typer.Option(WEB3_RPC, envvar="WEB3_RPC"),
    max_retries: str = typer.Option(MAX_RETRIES, envvar="MAX_RETRIES"),
    update_every_seconds: str = typer.Option(UPDATE_EVERY_SECONDS, envvar="UPDATE_EVERY_SECONDS"),
    sleep_before_continue: str = typer.Option(SLEEP_BEFORE_CONTINUE, envvar="SLEEP_BEFORE_CONTINUE"),
    explorer: str = typer.Option(EXPLORER, envvar="EXPLORER"),
    explorer_apikey: str = typer.Option(EXPLORER_APIKEY, envvar="EXPLORER_APIKEY"),
):
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
    rarity.send_all_to_adventure(lvl_up=lvlup)

if __name__ == "__main__":
    load_dotenv()
    typer.run(adventure)
