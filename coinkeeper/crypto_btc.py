import requests
import random
import cryptocode
from bitcoin import *
import bitcoin


def get_exchange_rate():
    """ takes no arguments and returnes exchange_rate for btc - usd """

    url = 'https://api.coingecko.com/api/v3/simple/price'
    params = {
        'ids': 'bitcoin',
        'vs_currencies': 'usd'
    }
    response = requests.get(url, params=params)
    data = response.json()
    exchange_rate = data['bitcoin']['usd']
    return exchange_rate


def get_btc_balance(address):
    """Takes one argument address and returns the btc address balance as a
    variable "balance_usd" and the btc balance as a variable "balance_btc" """

    # API endpoint for retrieving balance
    url = f"https://blockchain.info/balance?active={address}"

    try:
        response = requests.get(url)
        data = response.json()

        # Extract balance from the API response
        balance_btc = data[address]['final_balance'] * 1e-8
        balance_usd = balance_btc * get_exchange_rate()

    except requests.exceptions.RequestException as e:
        print(f"Error retrieving BTC balance: {e}")

        balance_usd = 0.0
        balance_btc = 0.0

    # Return the balances
    return balance_usd, balance_btc


def get_transaction_history(wallet_address):
    # Example data for test purposes
    example_data = [
        {"date": "2023-06-20", "address": "1KgA9oTRbn1HXXrXJvSjEfUNZ5DTacU2Ky", "BTC_value": "0.1", "USD_value": "3000"},
        {"date": "2023-06-25", "address": "1KgA9oTRbn1HXXrXJvSjEfUNZ5DTacU2Ky", "BTC_value": "0.02", "USD_value": "750"},
        {"date": "2023-07-01", "address": "13FayYiJ6LPVqiYMsuM4Qx7piuGY3LjtVA", "BTC_value": "0.05", "USD_value": "1500"},
        {"date": "2023-08-05", "address": "19yoPQH9PgrTq9r7Ee8mL2emUmxyVUmhrS", "BTC_value": "0.08", "USD_value": "1200"},
        {"date": "2023-08-13", "address": "1KgA9oTRbn1HXXrXJvSjEfUNZ5DTacU2Ky", "BTC_value": "0.07", "USD_value": "1800"},
        {"date": "2023-09-04", "address": "13VRMQX9N7i9EkRyw5PR75TxKNZAfCwzBZ", "BTC_value": "0.03", "USD_value": "900"},
    ]
    # API endpoint for retrieving transaction history
    url = f"https://blockstream.info/api/address/{wallet_address}/txs"
    response = requests.get(url)
    if response.status_code == 200:
        if not response.json():
            return example_data
        return response.json()
    else:
        return example_data


def create_BTC_keys(encryption_password):
    """takes one argument encryption_password and returns btc wallet keys and encrypts the private key"""
    # create Private Key
    private_key = random_key()
    #create public key
    public_key = privtopub(private_key)
    # create a Bitcoin address
    address = pubtoaddr(public_key)

    # encrypting the private key
    encrypted_private_key = cryptocode.encrypt(private_key,encryption_password)

    return encrypted_private_key, public_key, address


def is_valid_btc_address(address):
    """this needs completing"""
    return True


def send_transaction(send_to=None, from_address=None, amount=None):
    """this is a test function and will be replayced"""
    if send_to is None and from_address is None:
        btc_fee = 0.0005
        usd_fee = btc_fee * get_exchange_rate()
        return float(btc_fee), round(float(usd_fee))

    # Replace the code below with the actual transaction code using an API
    if send_to is not None and from_address is not None and amount is not None:
        return True

    return False  # Invalid input


def decrypt(enc_private_key, password):
    try:
        dec_private_key = cryptocode.decrypt(enc_private_key, password)
        return dec_private_key
    except Exception as e:
        print(f"Error during decryption: {str(e)}")
        return None
