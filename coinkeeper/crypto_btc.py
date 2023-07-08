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

    # Get exchange rate
    exchange_rate = get_exchange_rate()

    # API endpoint for retrieving balance
    url = f"https://blockchain.info/balance?active={address}"

    try:
        response = requests.get(url)
        data = response.json()

        # Extract balance from the API response
        balance_btc = data[address]['final_balance'] * 1e-8
        balance_usd = balance_btc * exchange_rate

    except requests.exceptions.RequestException as e:
        print(f"Error retrieving BTC balance: {e}")

        balance_usd = 0.0
        balance_btc = 0.0

    # Return the balances
    return balance_usd, balance_btc


def get_transaction_history(wallet_address):
    # API endpoint for retrieving transaction history
    url = f"https://blockstream.info/api/address/{wallet_address}/txs"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        # Example data for test perposes
        example_data = [
            {"date": "2023-07-01", "address": "1Kqd9KRbGyA8xQrrVMoGWPzy6YJ3ZEo7Pu", "amount": "0.05"},
            {"date": "2023-06-30", "address": "13VRMQX9N7i9EkRyw5PR75TxKNZAfCwzBZ", "amount": "0.02"},
            {"date": "2023-06-29", "address": "1Kqd9KRbGyA8xQrrVMoGWPzy6YJ3ZEo7Pu", "amount": "0.1"},
        ]
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
    if send_to is None and from_address is None and amount is None:
        btc_fee = "0.005" # replace with realtime fee
        return btc_fee  # Replace X with the actual fee amount

    # Replace the code below with the actual transaction code using a API
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
