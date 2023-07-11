from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import NoTransition, FadeTransition, Screen, ScreenManager
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.scrollview import ScrollView
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.filemanager import MDFileManager
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.metrics import dp
from kivy.clock import Clock
import matplotlib.pyplot as plt
from datetime import date
from datetime import datetime
import pyperclip
import json
import os
import socket
import urllib.request
from crypto_btc import *

from kivymd.theming import ThemeManager
from kivymd.toast import toast

Builder.load_file('static/login.kv')
Builder.load_file('static/home.kv')
Builder.load_file('static/wallet_bubble.kv')
Builder.load_file('static/new_wallet.kv')
Builder.load_file('static/create_account.kv')
Builder.load_file('static/wallet.kv')
Builder.load_file('static/Withdraw.kv')
Builder.load_file('static/settings.kv')
Builder.load_file('static/transaction_history.kv')
Builder.load_file('static/user_history.kv')

Clock.max_iteration = 70 # iteration limit


def show_popup(title, message, size=(400, 200)):
    """Display a popup with the given title and message.

    :param str title: The title of the popup.
    :param str message: The message to be displayed in the popup.
    :param tuple[int, int] size: The size of the popup window (width, height).
    """
    dialog = MDDialog(
        title=title,
        text=message,
        size_hint=(None, None),
        size=size,
    )
    dialog.open()


def confirm_popup(title, message, action, size=(400, 200)):
    """Display a popup with the given title, message, and confirm and cancel buttons.

    :param str title: The title of the popup.
    :param str message: The message to be displayed in the popup.
    :param function action: The function to be called when the confirm button is pressed.
    :param tuple[int, int] size: The size of the popup window (width, height).
    """
    dialog = MDDialog(
        title=title,
        text=message,
        size_hint=(None, None),
        size=size,
        buttons=[
            MDFlatButton(text="Continue", on_release=lambda x: action(dialog)),
            MDFlatButton(text="Cancel", on_release=lambda x: dialog.dismiss())
        ],
    )
    dialog.open()


def open_file(file_name, mode="r"):
    """Open the specified file and return its contents as a dictionary.

    :param str file_name: The name of the file to be opened.
    :param str type: The mode in which the file should be opened (default: "r").
    :return: The contents of the file as a dictionary.
    :rtype: dict
    """
    try:
        with open(file_name, mode) as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}
    return data


def save_file(file_name, data):
    """Save the given data to the specified file.

    :param str file_name: The name of the file to which the data should be saved.
    :param data: The data to be saved.
    """
    with open(file_name, "w") as file:
        json.dump(data, file)


def download_table(table_data, file_name):
    """Download the contents of the given table to the user's downloads directory.

    :param table_data: The data to be downloaded.
    :param str file_name: The name of the file to be created for the downloaded data.
    """
    if table_data:
        file_path = os.path.join(os.path.expanduser("~"), "Downloads", file_name)
        with open(file_path, "w") as output_file:
            json.dump(table_data, output_file)
        show_popup(title="Download", message=f"Exported data to: {file_path}", size=(500, 300))
    else:
        show_popup(title="Error", message="No data to download.")


def calculate_days(open_date, unlock_date):
    """Calculate the number of days remaining between the open_date and unlock_date.

    :param str open_date: The date the wallet was opened (format: "YYYY-MM-DD").
    :param str unlock_date: The date the wallet will be unlocked (format: "YYYY-MM-DD").
    :return: A tuple containing the number of days elapsed, the maximum number of days, and the wallet status.
    :rtype: tuple[int, int, str]
    """
    open_datetime = datetime.strptime(open_date, "%Y-%m-%d")
    unlock_datetime = datetime.strptime(unlock_date, "%Y-%m-%d")
    current_datetime = datetime.now().date()
    max_datetime = unlock_datetime.date()
    current_days = (current_datetime - open_datetime.date()).days
    max_days = (max_datetime - open_datetime.date()).days
    status = "Locked" if current_days < max_days else "Unlocked"
    return current_days, max_days, status


def check_file_entries(file_path):
    """Check the entries in the specified file and return wallet information if valid.

    :param str file_path: The path to the file to be checked.
    :return: Wallet information if all required entries are present, otherwise False.
    :rtype: dict or bool
    """
    data = open_file(file_path, mode="r")
    data_type = 0
    wallet_info = {}
    for wallet_name, entry_value in data.items():
        if entry_value:
            data_type += 1
            wallet_info[wallet_name] = data.get(wallet_name)
    if data_type == 8:
        return wallet_info
    return False


def save_wallet(wallet_info):
    """Save the wallet information to the wallet_data.json file.

    :param dict wallet_info: The wallet information to be saved.
    """
    data = open_file(file_name="data/wallet_data.json", mode="r")
    data[wallet_info["wallet_name"]] = wallet_info
    with open('data/wallet_data.json', 'w') as file:
        json.dump(data, file)


def add_history(event_type, info=None):
    """Save the user's history with the specified event type and additional information.

    :param str event_type: The type of the event.
    :param str info: Additional information related to the event (default: None).
    """
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime('%H:%M:%S')
    event_messages = {
        "new_account": "New Account Created",
        "login": "User Logged in",
        "new_wallet": f"Created New Wallet - {info}",
        "del_wallet": f"Deleted Wallet - {info}",
        "update_app": "Updated App Settings",
        "user_info": "Updated User Info",
        "new_password": "Changed Password"
    }
    message = event_messages.get(event_type)
    user_data = {"date": f"{current_date} {current_time}", "event": message}
    try:
        with open("data/user_history.json", "r") as file:
            existing_data = json.load(file)
    except FileNotFoundError:
        existing_data = {"history": []}
    updated_data = [user_data] + existing_data.get("history", [])
    with open("data/user_history.json", "w") as file:
        json.dump({"history": updated_data}, file)
