from datetime import datetime
from time import sleep

import web3
from web3.main import Web3

from rarity.constants import COLORS
from rarity.constants import EXPLORER
from rarity.constants import MAX_RETRIES
from rarity.constants import SLEEP_BEFORE_CONTINUE
from rarity.constants import UPDATE_EVERY_SECONDS
from rarity.constants import WEB3_RPC
from rarity.utils import format_timedelta
from rarity.utils import nonce
from rarity.utils import sign_and_send_txn
from rarity.utils import tx_explorer_link


class Summoner:
    def __init__(
        self,
        private_key,
        address,
        rarity_address,
        abi,
        summoner_id,
        web3_rpc=WEB3_RPC,
        max_retries=MAX_RETRIES,
        update_every_seconds=UPDATE_EVERY_SECONDS,
        sleep_before_continue=SLEEP_BEFORE_CONTINUE,
        explorer=EXPLORER,
    ):
        self.web3 = Web3(Web3.HTTPProvider(web3_rpc))
        self.private_key = private_key
        self.address = Web3.toChecksumAddress(address)
        self.rarity_address = Web3.toChecksumAddress(rarity_address)
        self.contract = self.web3.eth.contract(
            address=self.rarity_address, abi=abi)
        self.summoner_id = summoner_id
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
            adventure_txn = self.contract.functions.adventure(
                self.summoner_id
            ).buildTransaction({'nonce': nonce(self.web3, self.address)})
            tx_hash = sign_and_send_txn(
                self.web3, adventure_txn, self.private_key)
            self.log(
                f'Sending to adventure! {tx_explorer_link(self.explorer, tx_hash)}'
            )
            return tx_hash
        except web3.exceptions.ContractLogicError:
            self.log('is sleeping!')

    def lvl_up(self):
        try:
            lvlup_txn = self.contract.functions.level_up(
                self.summoner_id
            ).buildTransaction({'nonce': nonce(self.web3, self.address)})
            tx_hash = sign_and_send_txn(self.web3, lvlup_txn, self.private_key)
            self.log(
                f'Leveling UP! {tx_explorer_link(self.explorer, tx_hash)}')
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
                    self.log(
                        f'Adventure TX take too long to confirm! {tx_explorer_link(self.explorer, tx_hash)}'
                    )

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
                    self.log(
                        f'Level-up TX take too long to confirm! {tx_explorer_link(self.explorer, lvlup_tx_hash)}'
                    )

        remaining_time = self.remaining_time()
        formated_remaining_time = format_timedelta(remaining_time)
        self.log(
            f'is sleeping for {formated_remaining_time[0]} Hours and {formated_remaining_time[1]} Minutes'
        )
        return remaining_time
