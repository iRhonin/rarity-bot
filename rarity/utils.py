from urllib.parse import urljoin

import httpx

FTMSCAN_ERC721_URL= 'https://api.ftmscan.com/api?module=account&action=tokennfttx&address=%s&startblock=0&endblock=999999999&sort=asc&apikey=%s'


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

