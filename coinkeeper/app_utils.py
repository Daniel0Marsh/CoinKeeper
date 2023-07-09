from kivymd.app import MDApp
from kivy.lang import Builder
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
import matplotlib.pyplot as plt
from kivy.metrics import dp
from datetime import date
from datetime import datetime
from pandas.io import clipboard
from kivy.clock import Clock
import json
import os
import socket
from crypto_btc import *

from kivy.core.window import Window

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

Clock.max_iteration = 60 # Increase the iteration limit to 60 (or higher if needed)

def show_popup(title, message, size=(400, 200)):
    dialog = MDDialog(
        title=title,
        text=message,
        size_hint=(None, None),
        size=size,
    )

    dialog.open()


def confirm_popup(title, message, action, size=(400, 200)):
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

def open_file(file_name, type="r"):
    try:
        with open(file_name, type) as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}
    return data

def save_file(file_name, data):
    with open(file_name, "w") as file:
        json.dump(data, file)


def calculate_days(open_date, unlock_date):
    # Convert the date strings to datetime objects
    open_datetime = datetime.strptime(open_date, "%Y-%m-%d")
    unlock_datetime = datetime.strptime(unlock_date, "%Y-%m-%d")

    # Calculate the current date and the maximum date
    current_datetime = datetime.now().date()
    max_datetime = unlock_datetime.date()

    # Calculate the number of days that have passed
    current_days = (current_datetime - open_datetime.date()).days

    # Calculate the total number of days between open_date and unlock_date
    max_days = (max_datetime - open_datetime.date()).days

    # Compare current_days and max_days to determine the status
    if current_days < max_days:
        status = "Locked"
    else:
        status = "Unlocked"

    return current_days, max_days, status


def check_file_entries(file_path):
    data = open_file(file_path, type="r")
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
    data = open_file(file_name="data/wallet_data.json", type="r")
    data[wallet_info["wallet_name"]] = wallet_info
    with open('data/wallet_data.json', 'w') as file:
        json.dump(data, file)


def add_history(event_type, info=None):
    # Get today's date
    today = date.today()
    current_date = today.strftime("%Y-%m-%d")
    current_time = datetime.now().time().strftime('%H:%M:%S')

    # Define the message based on the event type and info
    if info:
        if event_type == "new_wallet":
            message = f"Created New Wallet - {info}"
        else:
            message = f"Deleted Wallet - {info}"
    else:
        if event_type == "login":
            message = "User Logged in"
        else:
            message = "New Account Created"


    # Create a dictionary with date and history message
    user_data = {"date": current_date +" "+ current_time, "event": message}

    try:
        # Load existing JSON data from the file
        with open("data/user_history.json", "r") as file:
            existing_data = json.load(file)
    except FileNotFoundError:
        existing_data = {"history": []}

    # Create a list to hold new and existing history data
    updated_data = [user_data]

    # Append the existing history data to the list
    if "history" in existing_data:
        updated_data.extend(existing_data["history"])

    # Update the JSON data with the updated list
    updated_json_data = json.dumps({"history": updated_data})

    # Save the updated JSON data to the file
    with open("data/user_history.json", "w") as file:
        file.write(updated_json_data)
