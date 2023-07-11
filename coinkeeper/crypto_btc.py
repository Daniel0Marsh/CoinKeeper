import requests
import random
import cryptocode
from bitcoin import *
import re
from kivymd.uix.dialog import MDDialog

# Define a global variable to keep track of the dialog instance
current_dialog = None

def no_connection():
    """Remove any existing popups and display a popup indicating no internet connection."""
    global current_dialog
    if current_dialog:
        current_dialog.dismiss()

    dialog = MDDialog(
        title="No Internet Connection",
        text="Unable to retrieve or update data such as transaction history or wallet balance.\n\nPlease check your internet connection and try again.",
        size_hint=(None, None),
        size=(400, 200))
    dialog.open()
    current_dialog = dialog


def get_exchange_rate():
    """Get the current exchange rate of Bitcoin (BTC) to USD (United States Dollar).

    :return: The current exchange rate.
    :rtype: float
    """
    try:
        url = 'https://api.coingecko.com/api/v3/simple/price'
        params = {
            'ids': 'bitcoin',
            'vs_currencies': 'usd'
        }
        response = requests.get(url, params=params)
        data = response.json()
        exchange_rate = data['bitcoin']['usd']
        return exchange_rate
    except requests.exceptions.RequestException:
        return 0


def get_btc_balance(address):
    """Get the Bitcoin (BTC) address balance in USD and BTC.

    :param str address: The Bitcoin address to check.
    :return: The balance in USD and BTC.
    :rtype: tuple[float, float]
    """
    url = f"https://blockchain.info/balance?active={address}"
    try:
        response = requests.get(url)
        data = response.json()
        balance_btc = data[address]['final_balance'] * 1e-8
        balance_usd = balance_btc * get_exchange_rate()
    except requests.exceptions.RequestException:
        no_connection()
        balance_usd = 0.0
        balance_btc = 0.0
    return balance_usd, balance_btc


def get_transaction_history(wallet_address):
    """Get the transaction history for a Bitcoin (BTC) wallet address.

    :param str wallet_address: The Bitcoin wallet address.
    :return: The transaction history as a list of dictionaries.
    :rtype: list[dict] or None
    """
    url = f"https://blockstream.info/api/address/{wallet_address}/txs"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            if not response.json():
                return None
            return response.json()
        else:
            return None
    except requests.exceptions.RequestException:
        return None


def create_BTC_keys(encryption_password):
    """Create Bitcoin (BTC) wallet keys and encrypt the private key.

    :param str encryption_password: The password for encrypting the private key.
    :return: The encrypted private key, public key, and Bitcoin address.
    :rtype: tuple[str, str, str]
    """
    private_key = random_key()
    public_key = privtopub(private_key)
    address = pubtoaddr(public_key)
    encrypted_private_key = cryptocode.encrypt(private_key, encryption_password)
    return encrypted_private_key, public_key, address


def is_valid_btc_address(address):
    """Check if a Bitcoin (BTC) wallet address is valid.

    :param str address: The Bitcoin wallet address to check.
    :return: True if the address is valid, False otherwise.
    :rtype: bool
    """
    if not re.match(r"^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$", address):
        return False
    decoded_address = base58_decode(address)
    if not decoded_address:
        return False
    checksum = decoded_address[-4:]
    address_bytes = decoded_address[:-4]
    checksum_hash = double_sha256(address_bytes)[:4]
    if checksum != checksum_hash:
        return False
    return True


def api_send_transaction(from_address, send_to, amount):
    """Send a Bitcoin (BTC) transaction using the Blockstream API.

    :param str from_address: The sender's Bitcoin address.
    :param str send_to: The recipient's Bitcoin address.
    :param float amount: The amount to send in BTC.
    :return: "success" if the transaction is successful, "failure" otherwise.
    :rtype: str
    """
    try:
        endpoint = "https://blockstream.info/api/txs/new"
        payload = {
            "inputs": [
                {"address": from_address}
            ],
            "outputs": [
                {"address": send_to, "value": amount}
            ]
        }
        response = requests.post(endpoint, json=payload)
        if response.status_code == 200:
            return "success"
        else:
            return "failure"
    except requests.exceptions.RequestException:
        no_connection()
        return "failure"


def send_transaction(send_to=None, from_address=None, amount=None):
    """Send a Bitcoin (BTC) transaction from one address to another.

    :param str send_to: The recipient's Bitcoin address (default: None).
    :param str from_address: The sender's Bitcoin address (default: None).
    :param float amount: The amount to send in BTC (default: None).
    :return: True if the transaction is successful, False otherwise.
    :rtype: bool
    """
    if send_to is None and from_address is None:
        btc_fee = 0.0005  # Replace with the actual BTC fee
        usd_fee = btc_fee * get_exchange_rate()
        return float(btc_fee), round(float(usd_fee), 2)

    if send_to is not None and from_address is not None and amount is not None:
        transaction_result = api_send_transaction(from_address, send_to, amount)

        if transaction_result == "success":
            return True
        else:
            return False
    return False


def decrypt(enc_private_key, password):
    """Decrypt an encrypted private key using a password.

    :param str enc_private_key: The encrypted private key.
    :param str password: The password for decryption.
    :return: The decrypted private key or None if decryption fails.
    :rtype: str or None
    """
    try:
        dec_private_key = cryptocode.decrypt(enc_private_key, password)
        return dec_private_key
    except Exception as e:
        print(f"Error during decryption: {str(e)}")
        return None
