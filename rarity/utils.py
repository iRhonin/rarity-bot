import time
from datetime import datetime
from functools import wraps
from urllib.parse import urljoin

import httpx
from toolz.itertoolz import isiterable

from rarity.constants import FTMSCAN_ERC721_URL


def tx_explorer_link(explorer_link, tx_hash):
    return urljoin(explorer_link, f'/tx/{tx_hash}')


def format_timedelta(timedelta):
    hours, remainder = divmod(timedelta, 3600)
    minutes, seconds = divmod(remainder, 60)
    return int(hours), int(minutes), int(seconds)


def fetch_erc721(api_key, address):
    url = FTMSCAN_ERC721_URL % (address, api_key)

    with httpx.Client() as client:
        result = client.get(url)
        if result.status_code != 200 or result.json()['status'] != '1':
            return

        return result.json()['result']


def sign_and_send_txn(web3, txn, private_key):
    signed_txn = web3.eth.account.sign_transaction(txn, private_key)
    web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_hash = web3.toHex(web3.keccak(signed_txn.rawTransaction))
    return tx_hash


def nonce(web3, address):
    return web3.eth.getTransactionCount(address, 'pending')


def retry_call(
    f,
    *args,
    _retries=5,
    _delay=3,
    _excluded=[],
    **kwargs,
):

    if not isiterable(_excluded):
        _excluded = [_excluded]

    while True:
        try:
            return f(*args, **kwargs)
        except Exception as ex:
            if ex in _excluded or _retries <= 0:
                raise

            _retries -= 1
            time.sleep(_delay)


def retry(retries=10, delay=5):
    def _retry(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            return retry_call(
                f,
                *args,
                _retries=retries,
                _delay=delay,
                _excluded=[],
                **kwargs,
            )

        return wrapper

    if callable(retries):
        retries = 10
        delay = 5
        return _retry(retries)
    else:
        return _retry


def wait_for_confirmation(web3, tx_hash, timeout=60, delay=5) -> int:
    """Wait for a tx to confirm, returns block number if confirmed, raise otherwise

    Args:
        web3 (Web3): Web3 object
        tx_hash (str): Transaction hash
        timeout (int, optional): Seconds. Defaults to 60.
        delay (int, optional): Seconds. Defaults to 5.

    Raises:
        TimeoutError

    Returns:
        int: block number

    """
    deadline = datetime.utcnow().timestamp() + timeout

    while datetime.utcnow().timestamp() <= deadline:
        tx = web3.eth.getTransaction(tx_hash)
        if tx and tx['blockNumber'] is not None:
            return tx['blockNumber']

        time.sleep(delay)

    raise TimeoutError()
