import math
import json
from web3 import Web3, Account


class BSC:
    def __init__(self, private_key, address):
        self.private_key = private_key
        self.address = address
        self.w3 = Web3(Web3.HTTPProvider('https://bsc-dataseed.binance.org'))
        self.contract_address = '0xB72a20C7B8BD666f80AC053B0f4de20a787080F5'
        self.token_abi = json.loads('[{"inputs":[{"internalType":"string","name":"name","type":"string"},{"internalType":"string","name":"symbol","type":"string"},{"internalType":"uint256","name":"totalSupply_","type":"uint256"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"spender","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"user","type":"address"}],"name":"RestrictUser","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"user","type":"address"}],"name":"UnrestrictUser","type":"event"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"subtractedValue","type":"uint256"}],"name":"decreaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"addedValue","type":"uint256"}],"name":"increaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"user","type":"address"}],"name":"restrictUser","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"restrictedUsers","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"user","type":"address"}],"name":"unrestrictUser","outputs":[],"stateMutability":"nonpayable","type":"function"}]')

        self.token_contract = self.w3.eth.contract(address=self.contract_address, abi=self.token_abi)

    def _create_transaction(self, recipient, value):
        try:
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
            return True, tx
        except Exception as e:
            return False, str(e)

    def _create_token_transaction(self, recipient, value):
        try:
            tx_data = self.token_contract.functions.transfer(recipient, self.w3.to_wei(value, 'ether')).build_transaction({
                'chainId': 56,
                'from': self.address,
                'gas': 210000,
                'gasPrice': self.w3.to_wei('5', 'gwei'),
                'nonce': self.w3.eth.get_transaction_count(self.address)
            })
            gas_estimate = self.w3.eth.estimate_gas(tx_data)
            tx_data['gas'] = gas_estimate
            return True, tx_data
        except Exception as e:
            return False, str(e)

    def send_transaction(self, recipient, value):
        try:
            success, tx = self._create_transaction(recipient, value)
            if success:
                signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
                tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                return True, self.w3.to_hex(tx_hash)
            else:
                return success, tx
        except Exception as e:
            return False, str(e)

    def send_token_transaction(self, recipient, value):
        try:
            success, tx_data = self._create_token_transaction(recipient, value)
            if success:
                signed_tx = self.w3.eth.account.sign_transaction(tx_data, self.private_key)
                tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                return True, self.w3.to_hex(tx_hash)
            else:
                return success, tx_data
        except Exception as e:
            return False, str(e)

    def balance(self, _round=8):
        return math.floor(self.w3.eth.get_balance(self.address)/pow(10, 18) * 10 ** _round) / 10 ** _round

    def balance_of_token(self, _round=8):
        try:
            balance = self.token_contract.functions.balanceOf(self.address).call()
            balance_in_mlt = self.w3.from_wei(balance, 'ether')
            return balance_in_mlt
        except Exception as e:
            return str(e)

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

