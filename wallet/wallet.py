import math
from web3 import Web3, Account


class BSC:
    def __init__(self, private_key, address):
        self.private_key = private_key
        self.address = address
        self.w3 = Web3(Web3.HTTPProvider('https://bsc-dataseed.binance.org'))

    def _create_transaction(self, recipient, value):
        tx = {
            'from': self.address,
            'to': recipient,
            'value': self.w3.to_wei(value, 'ether'),
            'gas': 21000,
            'gasPrice': self.w3.to_wei('5', 'gwei'),
            'nonce': self.w3.eth.get_transaction_count(self.address)
        }
        gas_estimate = self.w3.eth.estimate_gas(tx)
        tx['gas'] = gas_estimate
        return tx

    def send_transaction(self, recipient, value):
        try:
            signed_tx = self.w3.eth.account.sign_transaction(self._create_transaction(recipient, value), self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            return True, self.w3.to_hex(tx_hash)
        except ValueError:
            return False, 'insufficient funds for transfer'

    def balance(self, _round=8):
        return math.floor(self.w3.eth.get_balance(self.address)/pow(10, 18) * 10 ** _round) / 10 ** _round

    def status_transaction(self, tx):
        tx = self.w3.eth.get_transaction(tx)

        if tx and tx['blockHash']:
            return True
        else:
            return False


def mnemonic_to_creds(mnemonic):
    Account.enable_unaudited_hdwallet_features()
    account = Account.from_mnemonic(mnemonic)
    return account.address, account._private_key.hex()
