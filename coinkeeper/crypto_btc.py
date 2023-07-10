import requests
import random
import cryptocode
from bitcoin import *
import re
from kivymd.uix.dialog import MDDialog

# Define a global variable to keep track of the dialog instance
current_dialog = None

def no_connection():
    global current_dialog
    if current_dialog:  # Check if a dialog is already open
        current_dialog.dismiss()  # Dismiss the current dialog if it exists

    dialog = MDDialog(
        title="No Internet Connection",
        text="Unable to retrieve or update data such as transaction history or wallet balance.\n\nPlease check your internet connection and try again.",
        size_hint=(None, None),
        size=(400, 200),
    )

    dialog.open()

    current_dialog = dialog



def get_exchange_rate():
    """Get the current exchange rate of BTC to USD."""
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
    """Get the BTC address balance in USD and BTC."""

    # API endpoint for retrieving balance
    url = f"https://blockchain.info/balance?active={address}"

    try:
        response = requests.get(url)
        data = response.json()

        # Extract balance from the API response
        balance_btc = data[address]['final_balance'] * 1e-8
        balance_usd = balance_btc * get_exchange_rate()

    except requests.exceptions.RequestException:
        no_connection()
        balance_usd = 0.0
        balance_btc = 0.0

    # Return the balances
    return balance_usd, balance_btc




def get_transaction_history(wallet_address):
    """Get the transaction history for a wallet address."""

    # Example data for test purposes
    example_data = [
        {"date": "2023-06-20", "address": "1KgA9oTRbn1HXXrXJvSjEfUNZ5DTacU2Ky", "BTC_value": "0.1", "USD_value": "3000"},
        {"date": "2023-06-25", "address": "1KgA9oTRbn1HXXrXJvSjEfUNZ5DTacU2Ky", "BTC_value": "0.02", "USD_value": "750"},
        {"date": "2023-07-01", "address": "13FayYiJ6LPVqiYMsuM4Qx7piuGY3LjtVA", "BTC_value": "0.05", "USD_value": "1500"},
        {"date": "2023-08-05", "address": "19yoPQH9PgrTq9r7Ee8mL2emUmxyVUmhrS", "BTC_value": "0.08", "USD_value": "1200"},
        {"date": "2023-08-13", "address": "1KgA9oTRbn1HXXrXJvSjEfUNZ5DTacU2Ky", "BTC_value": "0.07", "USD_value": "1800"},
        {"date": "2023-09-04", "address": "13VRMQX9N7i9EkRyw5PR75TxKNZAfCwzBZ", "BTC_value": "0.03", "USD_value": "900"},
    ]

    try:
        # API endpoint for retrieving transaction history
        url = f"https://blockstream.info/api/address/{wallet_address}/txs"
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
    """Create BTC wallet keys and encrypt the private key."""

    # create Private Key
    private_key = random_key()
    # create public key
    public_key = privtopub(private_key)
    # create a Bitcoin address
    address = pubtoaddr(public_key)

    # encrypting the private key
    encrypted_private_key = cryptocode.encrypt(private_key, encryption_password)

    return encrypted_private_key, public_key, address


def is_valid_btc_address(address):
    """Check if a BTC wallet address is correct and return True or False."""

    # Check if the address matches the expected format
    if not re.match(r"^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$", address):
        return False

    # Perform additional verification using checksum
    decoded_address = base58_decode(address)
    if not decoded_address:
        return False

    # Verify the checksum
    checksum = decoded_address[-4:]
    address_bytes = decoded_address[:-4]
    checksum_hash = double_sha256(address_bytes)[:4]
    if checksum != checksum_hash:
        return False

    return True


def api_send_transaction(from_address, send_to, amount):
    """Send a Bitcoin transaction using the Blockstream API."""
    # Implement the function to send the transaction using the Blockstream API
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
    """Send a Bitcoin transaction from one address to another."""

    if send_to is None and from_address is None:
        btc_fee = 0.0005  # Replace with the actual BTC fee
        usd_fee = btc_fee * get_exchange_rate()
        return float(btc_fee), round(float(usd_fee), 2)

    # transaction code using an API
    if send_to is not None and from_address is not None and amount is not None:
        transaction_result = api_send_transaction(from_address, send_to, amount)

        if transaction_result == "success":
            return True
        else:
            return False

    return False  # Invalid input


def decrypt(enc_private_key, password):
    """Decrypt an encrypted private key using a password."""

    try:
        dec_private_key = cryptocode.decrypt(enc_private_key, password)
        return dec_private_key
    except Exception as e:
        print(f"Error during decryption: {str(e)}")
        return None
