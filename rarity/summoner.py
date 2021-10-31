from datetime import datetime
from time import sleep

import web3
from web3.main import Web3

from rarity.constants import COLORS
from rarity.constants import DEFAULT_GAS_LIMIT
from rarity.constants import EXPLORER
from rarity.constants import MAX_RETRIES
from rarity.constants import SLEEP_BEFORE_CONTINUE
from rarity.constants import WEB3_RPC
from rarity.utils import format_timedelta
from rarity.utils import nonce
from rarity.utils import retry
from rarity.utils import retry_call
from rarity.utils import sign_and_send_txn
from rarity.utils import tx_explorer_link
from rarity.utils import wait_for_confirmation


class Summoner:
    def __init__(
        self,
        private_key,
        address,
        contract,
        summoner_id,
        web3_rpc=WEB3_RPC,
        max_retries=MAX_RETRIES,
        sleep_before_continue=SLEEP_BEFORE_CONTINUE,
        explorer=EXPLORER,
    ):
        self.web3 = Web3(Web3.HTTPProvider(web3_rpc))
        self.private_key = private_key
        self.address = Web3.toChecksumAddress(address)
        self.contract = contract
        self.summoner_id = summoner_id
        self.max_retries = max_retries
        self.sleep_before_continue = sleep_before_continue
        self.explorer = explorer

    def _retry_call(self, f, *args, **kwargs):
        return retry_call(
            f,
            *args,
            **kwargs,
            _retries=self.max_retries,
            _delay=self.sleep_before_continue,
        )

    def nonce(self):
        return self._retry_call(
            nonce,
            self.web3,
            self.address,
        )

    def log(self, msg):
        color = COLORS[self.summoner_id % len(COLORS)]
        print(f'{color}Summoner #{self.summoner_id}: {msg}')

    def next_adventure_in(self):
        return self._retry_call(
            self.contract.functions.adventurers_log(self.summoner_id).call,
        )

    def remaining_time(self):
        next_adventure = self.next_adventure_in()
        timedelta = datetime.fromtimestamp(next_adventure) - datetime.now()
        return timedelta.total_seconds()

    def data(self):
        result = self._retry_call(self.contract.functions.summoner(self.summoner_id).call)

        data = dict(
            xp=result[0],
            log=result[1],
            class_=result[2],
            level=result[3],
        )
        self.log(f'XP: {data.get("xp")}, Level: {data.get("level")}')
        return data

    def do_adventure(self):
        # Setting gas manualy when web3 fails to estimate gas
        # https://github.com/iRhonin/rarity-bot/issues/2
        adventure_txn = self.contract.functions.adventure(
            self.summoner_id,
        ).buildTransaction({'gas': DEFAULT_GAS_LIMIT, 'nonce': self.nonce()})

        tx_hash = self._retry_call(
            sign_and_send_txn,
            self.web3,
            adventure_txn,
            self.private_key,
            _excluded=web3.exceptions.ContractLogicError,
        )
        self.log(f'Going to adventure! {tx_explorer_link(self.explorer, tx_hash)}')
        return tx_hash

    def lvl_up(self):
        lvlup_txn = self.contract.functions.level_up(
            self.summoner_id,
        ).buildTransaction({'gas': DEFAULT_GAS_LIMIT, 'nonce': self.nonce()})

        tx_hash = self._retry_call(
            sign_and_send_txn,
            self.web3,
            lvlup_txn,
            self.private_key,
            _excluded=web3.exceptions.ContractLogicError,
        )
        self.log(f'Leveling UP! {tx_explorer_link(self.explorer, tx_hash)}')
        return tx_hash

    def adventure(self, lvl_up=False):
        while self.remaining_time() <= 0:
            try:
                tx_hash = self.do_adventure()
                self._retry_call(
                    wait_for_confirmation,
                    web3=self.web3,
                    tx_hash=tx_hash,
                    timeout=self.max_retries * self.sleep_before_continue,
                    delay=self.sleep_before_continue,
                    _excluded=TimeoutError,
                )
                self.log(f'Did an adventure!')
                self.data()

                if lvl_up:
                    lvlup_tx_hash = self.lvl_up()
                    self._retry_call(
                        wait_for_confirmation,
                        web3=self.web3,
                        tx_hash=lvlup_tx_hash,
                        timeout=self.max_retries * self.sleep_before_continue,
                        delay=self.sleep_before_continue,
                        _excluded=TimeoutError,
                    )
                    self.data()
            except Exception as ex:
                print(ex)

        remaining_time = self.remaining_time()
        formated_remaining_time = format_timedelta(remaining_time)
        self.log(
            f'Sleeping for {formated_remaining_time[0]} Hours and {formated_remaining_time[1]} Minutes'
        )
        return remaining_time
