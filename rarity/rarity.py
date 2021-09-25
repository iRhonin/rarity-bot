from typing import List
from typing import Type

from eth_utils import address
from web3.main import Web3

from rarity.abis import RARITY_ABI
from rarity.constants import EXPLORER
from rarity.constants import EXPLORER_APIKEY
from rarity.constants import MAX_RETRIES
from rarity.constants import RARITY_ADRRESS
from rarity.constants import SLEEP_BEFORE_CONTINUE
from rarity.constants import UPDATE_EVERY_SECONDS
from rarity.constants import WEB3_RPC
from rarity.summoner import Summoner
from rarity.types import SummonerNextAdventure
from rarity.types import SummonerType
from rarity.utils import fetch_erc721
from rarity.utils import nonce
from rarity.utils import retry
from rarity.utils import retry_call
from rarity.utils import sign_and_send_txn


class Rarity:
    def __init__(
        self,
        private_key,
        address,
        web3_rpc=WEB3_RPC,
        rarity_address=RARITY_ADRRESS,
        abi=RARITY_ABI,
        summoners=None,
        max_retries=MAX_RETRIES,
        update_every_seconds=UPDATE_EVERY_SECONDS,
        sleep_before_continue=SLEEP_BEFORE_CONTINUE,
        explorer=EXPLORER,
        explorer_apikey=EXPLORER_APIKEY,
    ):
        self.web3_rpc = web3_rpc
        self.web3 = Web3(Web3.HTTPProvider(web3_rpc))
        self.summoners_thread_list = []
        self.summoners = []
        self.private_key = private_key
        self.address = Web3.toChecksumAddress(address)
        self.rarity_address = Web3.toChecksumAddress(rarity_address)
        self.contract = self.web3.eth.contract(address=self.rarity_address, abi=abi)
        self.abi = abi
        self.max_retries = int(max_retries)
        self.update_every_seconds = int(update_every_seconds)
        self.sleep_before_continue = int(sleep_before_continue)
        self.explorer = explorer
        self.explorer_apikey = explorer_apikey
        self.remaining_times = {}

        if summoners:
            summoner_ids = summoners
        else:
            print('Fetching summoners...')
            summoner_ids = self.fetch_summoners()
            print(
                'Found these summoners in the jungle: ',
                ' '.join([s for s in map(str, summoner_ids)]),
            )

        for summoner_id in summoner_ids:
            summoner = Summoner(
                web3_rpc=self.web3_rpc,
                private_key=self.private_key,
                address=self.address,
                contract=self.contract,
                summoner_id=summoner_id,
            )
            self.summoners.append(summoner)

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

    def fetch_summoners(self):
        """Fetch Rarity summoners from explorer

        Returns:
            [Sumomoner Ids]: An array of summoner id
        """

        erc721s = self._retry_call(
            fetch_erc721,
            self.explorer_apikey,
            self.address,
        )
        if erc721s is None:
            return []

        summoner_ids = [
            int(s['tokenID'])
            for s in erc721s
            if address.is_same_address(s['contractAddress'], self.rarity_address)
        ]
        return summoner_ids

    def send_all_to_adventure(self, lvl_up=False) -> List[SummonerNextAdventure]:
        """Send all summoners to adventure if possible

        Args:
            lvl_up (bool, optional): [lvl up summoner if possible]. Defaults to False.

        Returns:
            list of SummonerNextAdventure: [An array of SummonerNextAdventure type (summoner_id, remaining time until next adventure)]
        """

        remaining_times = []
        for summoner in self.summoners:
            remaining_times.append(
                SummonerNextAdventure(
                    id=summoner.summoner_id,
                    remaining_time=summoner.adventure(lvl_up),
                )
            )

        return remaining_times

    def summon(self, type_: SummonerType):
        """Summon a summoner

        Args:
            type_ (SummonerType): Type of summoner

        Returns:
            str: Hash of summon tx
        """
        txn = self.contract.functions.summon(type_).buildTransaction(
            {
                'nonce': self.nonce(),
                'from': self.address,
            }
        )
        return self._retry_call(sign_and_send_txn, self.web3, txn, self.private_key)
