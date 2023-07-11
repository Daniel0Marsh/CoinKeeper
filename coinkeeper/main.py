from app_utils import *


class LoginScreen(Screen):
    """The screen for user login."""

    def login(self, *args):
        """Validate the user's login credentials and switch to the home screen if successful.

        :param args: Additional positional arguments (ignored).
        """
        username = self.ids.username.text
        password = self.ids.password.text

        if username and password:
            try:
                with open("data/user_data.json", "r") as file:
                    json_data = file.read()

                if json_data:
                    user_data = json.loads(json_data)
                    stored_username = user_data.get("user_name")
                    stored_email = user_data.get("email")
                    stored_password = user_data.get("password")

                    if username in (stored_username, stored_email) and password == stored_password:
                        self.manager.current = "home"
                        self.clear()
                        add_history(event_type="login", info=None)
                    else:
                        self.clear()
                        show_popup(title="Login Error", message="Invalid login credentials")
                else:
                    self.clear()
                    show_popup(title="Login Error", message="User data not found")
            except FileNotFoundError:
                self.clear()
                show_popup(title="Login Error", message="User data file not found")
        else:
            self.clear()
            show_popup(title="Login Error", message="Please provide both username and password.", size=(500, 300))


    def forgotten_password(self):
        """Show a popup with instructions for recovering a forgotten password."""
        show_popup(title="Forgotten Password", message="Try logging in with your email instead or request a password change.", size=(700, 500))

    def clear(self):
        self.ids.username.text = ""
        self.ids.password.text = ""

class CreateAccountScreen(Screen):
    """The screen for creating a new user account."""

    def show_password(self):
        """Toggle the visibility of the password and change the icon.

        This method is called when the password icon is clicked.
        """
        password_field = self.ids.password
        password_field.password = not password_field.password
        password_icon = self.ids.password_icon
        password_icon.icon = "eye-off" if password_field.password else "eye"


    def show_confirm_password(self):
        """Toggle the visibility of the confirm password field and change the icon.

        This method is called when the password confirmation icon is clicked.
        """
        password_confirm_field = self.ids.password_confirm
        password_confirm_field.password = not password_confirm_field.password
        password_confirm_icon = self.ids.password_confirm_icon
        password_confirm_icon.icon = "eye-off" if password_confirm_field.password else "eye"


    def create_account(self):
        """Create a new user account with the provided information.

        If all fields are provided and the passwords match, the user account is created and saved to a JSON file.
        """
        first_name = self.ids.first_name.text
        last_name = self.ids.last_name.text
        email = self.ids.email.text
        password = self.ids.password.text
        password_confirm = self.ids.password_confirm.text
        switch_theme = False
        switch_notifications = False

        if all([first_name, last_name, email, password, password_confirm]):
            if password == password_confirm:
                user_name = f"{first_name}.{last_name}"
                user_data = {
                    "first_name": first_name,
                    "last_name": last_name,
                    "user_name": user_name,
                    "email": email,
                    "password": password,
                    "switch_theme": switch_theme,
                    "switch_notifications": switch_notifications,
                }
                json_data = json.dumps(user_data)
                try:
                    with open("data/user_data.json", "r") as file:
                        existing_data = json.load(file)
                        if existing_data.get("user_name"):
                            show_popup(title="Error", message="User data already exists.", size=(500, 300))
                        else:
                            with open("data/user_data.json", "w") as file:
                                file.write(json_data)
                            add_history(event_type="new_account", info=None)
                            self.manager.current = "home"
                except FileNotFoundError:
                    show_popup(title="Error", message="User data file not found", size=(500, 300))
            else:
                show_popup(title="Error", message="Passwords don't match", size=(500, 300))
        else:
            show_popup(title="Error", message="Please provide all fields.", size=(500, 300))


class HomeScreen(Screen):
    """The home screen displaying wallet information and user history."""

    def on_enter(self):
        """Called when the screen is entered.

        Reads wallet data from the JSON file and updates the screen.
        """
        super().on_enter()

        self.walletlist = self.ids['walletlist']
        data = open_file(file_name="data/wallet_data.json", mode="r")
        self.update_screen(data)


    def update_screen(self, data):
        """Updates the screen with wallet information and user history.

        Clears the existing widgets from the wallet list and adds wallet bubbles for each wallet.
        Displays a label bubble if there are no wallets.
        Loads the user history from a JSON file and creates a table to display the recent user history.

        :param dict data: The wallet data.
        """
        self.walletlist.clear_widgets()

        for wallet_name, wallet_data in data.items():
            address = wallet_data.get('address', '')
            wallet_bubble = WalletBubble(name=wallet_name, address=address)
            self.walletlist.add_widget(wallet_bubble)

        if not data:
            label_bubble = LabelBubble(text="You have no wallets. Create one to view it here!")
            self.walletlist.add_widget(label_bubble)

        with open("data/user_history.json", "r") as file:
            existing_data = json.load(file)

        history_data = existing_data["history"]

        column_data = [
            ("Recent User History", dp(80)),
            ("", dp(50)),
        ]

        row_data = [
            (
                event["event"],
                ("history", event["date"])
            )
            for i, event in enumerate(history_data[:5])
        ]

        history_table = MDDataTable(
            column_data=column_data,
            row_data=row_data,
            elevation=2,
        )

        table = self.ids.table
        table.clear_widgets()
        table.add_widget(history_table)


class UserHistoryScreen(Screen):
    """The screen displaying the user's history."""

    def on_enter(self):
        """Called when the screen is entered.

        Reads wallet data from the JSON file and updates the screen.
        """
        super().on_enter()
        data = open_file(file_name="data/wallet_data.json", mode="r")
        self.update_screen(data)


    def update_screen(self, data):
        """Updates the screen with user history.

        Loads the user history from a JSON file and creates a table to display the history data.

        :param dict data: The wallet data.
        """
        with open("data/user_history.json", "r") as file:
            existing_data = json.load(file)

        self.history_data = existing_data["history"]

        column_data = [
            ("User History", dp(80)),
            ("", dp(50)),
        ]

        row_data = [
            (
                event["event"],
                ("history", event["date"])
            )
            for event in self.history_data
        ]

        history_table = MDDataTable(
            use_pagination=True,
            column_data=column_data,
            row_data=row_data,
            elevation=2,
            check=True,
            rows_num=10,
        )

        table = self.ids.table
        table.clear_widgets()
        table.add_widget(history_table)


    def download(self):
        """Downloads the user history as a text file."""
        download_table(table_data=self.history_data, file_name="user_history.txt")


class NewWalletScreen(Screen):
    """The screen for creating a new wallet."""


    def show_password(self):
        """Toggle the visibility of the password and change the icon.

        This method is called when the password icon is clicked.
        """
        self.ids.password.password = not self.ids.password.password
        self.ids.password_icon.icon = "eye-off" if self.ids.password.password else "eye"


    def on_save(self, instance, value, date_range):
        """Event called when the "OK" dialog box button is clicked.

        :param instance: The instance of the date picker dialog.
        :param value: The selected date value.
        :param date_range: The selected date range (unused in this method).
        """
        self.ids.date_of_completion.text = str(value)


    def on_cancel(self, instance, value):
        """Event called when the "CANCEL" dialog box button is clicked.

        :param instance: The instance of the date picker dialog.
        :param value: The previously selected date value (unused in this method).
        """
        self.ids.date_of_completion.text = str(value)


    def show_date_picker(self):
        """Show a date picker dialog to select the unlock date."""
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_save, on_cancel=self.on_cancel)
        date_dialog.open()


    def create_wallet(self):
        """Create a new wallet with the provided information.

        Performs validation and wallet creation logic. Displays confirmation popup if necessary.
        """
        wallet_name = self.ids.wallet_name.text
        unlock_date = self.ids.date_of_completion.text
        target_value = self.ids.target_value.text
        password = self.ids.password.text
        target_value = target_value if target_value != '' else 0
        target_value = float(target_value)
        today = date.today()
        open_date = today.strftime("%Y-%m-%d")

        encrypted_private_key, public_key, address = create_BTC_keys(password)

        wallet_info = {
            "wallet_name": wallet_name,
            "open_date": open_date,
            "unlock_date": unlock_date,
            "target_value": target_value,
            "password": password,
            "public_key": public_key,
            "encrypted_private_key": encrypted_private_key,
            "address": address,
        }

        if self.check(wallet_info):
            if unlock_date != open_date and target_value != 0.0:
                def confirmed(dialog_instance):
                    dialog_instance.dismiss()
                    save_wallet(wallet_info)
                    self.clear()
                    add_history(event_type="new_wallet", info=wallet_name)
                    self.manager.current = "home"
                    toast("Wallet created succesfully")

                confirm_popup(
                    title="Warning",
                    message=f"You will NOT be able to withdraw funds from this wallet until either {unlock_date} or when the balance reaches ${float(target_amount)}.\n\nProceeding with this action implies your understanding of these conditions.\n\nDo you still wish to proceed?",
                    action=confirmed,
                    size=(600, 400)
                )
            else:
                save_wallet(wallet_info)
                self.clear()
                add_history(event_type="new_wallet", info=wallet_name)
                self.manager.current = "home"
                toast("Wallet created succesfully")

    def check(self, wallet_info):
        """Check if the provided wallet information is valid.

        Performs validation checks on the wallet information.

        :param dict wallet_info: The wallet information.
        :return: True if the wallet information is valid, False otherwise.
        :rtype: bool
        """
        data = open_file(file_name="data/wallet_data.json", mode="r")

        if any(value == "" for value in wallet_info.values()):
            show_popup(title="Error", message="Please provide all fields.", size=(500, 300))
            return False
        elif wallet_info["wallet_name"] in data:
            show_popup(title="Error", message="Wallet name already in use")
            return False

        return True

    def cancel(self):
        self.clear()
        self.manager.current = "home"


    def clear(self):
        """Clear the input fields."""
        self.ids.wallet_name.text = ""
        self.ids.date_of_completion.text = ""
        self.ids.target_value.text = ""
        self.ids.password.text = ""


    def help(self):
        """Show a help popup with instructions for creating a new wallet."""
        show_popup(
            title="Help",
            message="Please provide the following information:\n\n"
                    "- Wallet Name: The name of the wallet you want to create.\n\n"
                    "- Unlock Date: The date by which you plan to reach your target.\n\n"
                    "- Target Amount: The desired amount of funds you aim to accumulate in the wallet.\n\n"
                    "- Password: The password used to encrypt the private key. It will NOT be shown again.\n\n"
                    "- IMPORTANT: The wallet will only become accessible once the Unlock Date or the target amount has been reached.\n\n",
            size=(700, 700)
        )


class WalletScreen(Screen):
    """The wallet screen displaying wallet information and details."""

    def on_enter(self):
        """
        Called when the WalletScreen is entered.

        """
        super().on_enter()

        # Load the JSON data from the file
        data = open_file(file_name="data/wallet_data.json", mode="r")
        self.wallet_info = data.get(self.ids.name.text)

        # Set values
        self.address = self.wallet_info.get('address')
        self.target_amount = self.wallet_info.get('target_amount')
        self.balance_usd, self.balance_btc = get_btc_balance(self.address)

        # Prepare the transaction data for the line chart
        transactions = get_transaction_history(self.address)
        data = []
        if transactions is not None:
            for transaction in transactions:
                date_str = transaction.get('date')
                btc_value = float(transaction.get('BTC_value'))
                usd_value = float(transaction.get('USD_value'))
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
                data.append((date, btc_value, usd_value))

        # Create and add the line chart widget
        title = "Wallet Performance"
        chart = LineChart(data=data, title=title)
        self.ids.chart_container.clear_widgets()
        self.ids.chart_container.add_widget(chart)


    def switch_currency(self):
        """
        Switch the currency displayed in the balance title.

        """
        switch_currency = self.ids.switch_currency.active

        if switch_currency:
            self.ids.balance_title.text = f"Current Balance: {self.balance_btc}"
        else:
            self.ids.balance_title.text = f"Current Balance: ${self.balance_usd}"


    def delete(self, wallet_name):
        """
        Delete a wallet entry.

        Args:
            wallet_name (str): The name of the wallet entry to delete.

        """
        if self.ids.balance.text == "$0.0":
            def delete_action(dialog_instance):
                dialog_instance.dismiss()  # Close the popup dialog
                data = open_file(file_name="data/wallet_data.json", mode="r")
                wallet_info = data.get(wallet_name)
                del data[wallet_name]
                save_file(file_name="data/wallet_data.json", data=data)
                self.manager.current = "home"
                add_history(event_type="del_wallet", info=wallet_name)

            confirm_popup(title="Confirm Deletion", message="Are you sure you want to delete the wallet?", action=delete_action)
        else:
            show_popup(title="Error", message="This Wallet is not empty!", size=(500, 300))


    def withdraw(self):
        """
        Navigate to the WithdrawScreen.

        """
        if self.ids.status.text == "Wallet Status: Locked":
            show_popup(title="Withdraw", message="This Wallet is currently locked", size=(500, 300))
        else:
            self.manager.current = "Withdraw"


    def deposit(self):
        """
        Display a popup with the wallet address for deposit.

        """
        show_popup(title="Deposit", message=self.address, size=(500, 300), button_on=False)


    def download(self):
        """
        Download the wallet data as a JSON file.

        """
        # Load the JSON data from the file
        data = open_file(file_name="data/wallet_data.json", mode="r")

        # Find the entry connected to self.ids.status.text
        entry_data = data.get(self.ids.name.text)

        # Create a file for the selected entry
        file_name = f"{self.ids.name.text}_wallet_data.json"
        file_path = os.path.join(os.path.expanduser("~"), "Downloads", file_name)

        # Save the entry data to the file
        with open(file_path, "w") as output_file:
            json.dump(entry_data, output_file)

        # Show a popup message indicating successful download
        show_popup(title="Download", message=f"Exported data to: {file_path}", size=(500, 300))


class WithdrawScreen(Screen):
    """The screen for performing a withdrawal from a wallet."""

    def on_enter(self):
        """Called when the screen is entered."""
        super().on_enter()

        # Access the name value from the WalletScreen
        wallet_screen = self.manager.get_screen('wallet')
        name_value = wallet_screen.ids.name.text

        # Load the JSON data from the file
        data = open_file(file_name="data/wallet_data.json", mode="r")
        self.wallet_info = data.get(name_value)

        # Set values
        self.address = self.wallet_info.get('address')
        self.encrypted_private_key = self.wallet_info.get('encrypted_private_key')
        self.balance_usd, self.balance_btc = get_btc_balance(self.address)

        # Schedule the interval to update values every 60 seconds
        self.update_values()  # Initial call with the current TextInput instance


    def update_values(self):
        """Update the displayed values based on the input field values."""
        self.amount = self.ids.amount.text
        self.btc_fee, self.usd_fee = send_transaction(send_to=None, from_address=None, amount=self.amount)
        self.gross_cost = self.usd_fee + self.balance_usd

        # Update values
        self.ids.balance_title.text = f"Available Balance: ${self.balance_usd}"
        self.ids.fee.text = f"Sending Fee: ${self.usd_fee}"
        self.ids.gross_cost.text = f"Net Cost: ${self.gross_cost}"
        self.ids.amount.icon_right = "currency-usd"


    def cancel(self):
        """Cancel the withdrawal and return to the wallet screen."""
        self.clear()
        self.manager.current = "wallet"


    def send(self):
        """Send the withdrawal transaction."""
        amount = self.ids.amount.text
        password = self.ids.password.text
        address = self.ids.address.text

        if amount and password and address:
            if float(amount) < self.balance_usd and float(amount) != 0:
                if is_valid_btc_address(address):
                    dec_private_key = decrypt(self.encrypted_private_key, password)
                    if dec_private_key:
                        if send_transaction(send_to=address, from_address=dec_private_key, amount=amount):
                            self.manager.current = "wallet"
                            toast("Withdrawal succesfully")
                            self.clear()
                        else:
                            show_popup(title="Error", message="Network Error, please try again later.", size=(500, 300))
                    else:
                        show_popup(title="Error", message="Incorrect password", size=(500, 300))
                else:
                    show_popup(title="Error", message="Invalid Bitcoin address", size=(500, 300))
            else:
                show_popup(title="Error", message="Insufficient funds", size=(500, 300))
        else:
            show_popup(title="Error", message="Please provide all fields.", size=(500, 300))


    def help(self):
        """Show a help popup with instructions for performing a withdrawal."""
        message = "To send a transaction, fill in the following fields:\n\n"
        message += "- Amount: Enter the amount of Bitcoin you want to send.\n"
        message += "- Password: Provide your password to decrypt the private key.\n"
        message += "- Address: Specify the recipient's Bitcoin address.\n\n"
        message += "Once you have filled in all the fields, click the 'Send' button to proceed with the transaction.\n"
        message += "Please make sure to double-check the recipient's address before sending.\n\n"
        message += "If you encounter any issues or errors, please refer to the error messages displayed or contact our support team for assistance."
        show_popup(title="Help", message=message, size=(500, 300))


    def change_currency(self):
        """Toggle between USD and BTC currency for displayed values."""
        if self.ids.balance_title.text == f"Available Balance: ${self.balance_usd}":
            self.ids.balance_title.text = f"Available Balance: {self.balance_btc}"
            self.ids.fee.text = f"Sending Fee: {self.btc_fee}"
            self.gross_cost = self.btc_fee + self.balance_btc
            self.ids.gross_cost.text = f"Net Cost: {self.gross_cost}"
            self.ids.amount.icon_right = "currency-btc"
        else:
            self.ids.balance_title.text = f"Available Balance: ${self.balance_usd}"
            self.ids.amount.icon_right = "currency-usd"
            self.ids.fee.text = f"Sending Fee: ${self.usd_fee}"
            self.gross_cost = self.usd_fee + self.balance_usd
            self.ids.gross_cost.text = f"Net Cost: ${self.gross_cost}"


    def set_amount(self, value):
        """Set the withdrawal amount based on the specified value.

        :param float value: The value used to calculate the withdrawal amount.
        """
        if self.balance_usd > 0.0:
            self.ids.amount.text = str(self.balance_usd / value)


    def clear(self):
        """Clear the input fields."""
        self.ids.amount.text = ""
        self.ids.password.text = ""
        self.ids.address.text = ""


class TransactionHistoryScreen(Screen):
    """The screen for displaying the transaction history of a wallet."""

    def on_enter(self):
        """Called when the screen is entered."""
        super().on_enter()

        # Access the name value from the WalletScreen
        wallet_screen = self.manager.get_screen('wallet')
        name_value = wallet_screen.ids.name.text
        table = self.ids.table

        # Load the JSON data from the file
        with open("data/wallet_data.json", "r") as file:
            data = json.load(file)
        self.wallet_info = data.get(name_value)

        # Set values
        self.address = self.wallet_info.get('address')

        # Example data for transaction history
        transaction_data = get_transaction_history(self.address)

        column_data = [
            ("Date", dp(30)),
            ("Sent/Received from", dp(80)),
            ("BTC value", dp(30)),
            ("USD value", dp(30)),
        ]

        row_data = []
        if transaction_data:
            for transaction in transaction_data:
                row_data.append(
                    (
                        transaction["date"],
                        ("arrow-bottom-right-bold-box", transaction["address"])
                        if self.address == transaction["address"]
                        else ("arrow-top-left-bold-box", [255 / 256, 165 / 256, 0, 1], transaction["address"]),
                        ("currency-btc", transaction["BTC_value"]),
                        ("currency-usd", transaction["USD_value"])
                    )
                )


        data_table = MDDataTable(
            use_pagination=True,
            column_data=column_data,
            row_data=row_data,
            elevation=2,
            check=True,
            rows_num=10,
        )

        # Clear and add the table widget
        table.clear_widgets()
        table.add_widget(data_table)


    def download(self):
        """Download the transaction history as a text file."""
        transaction_data = get_transaction_history(self.address)

        download_table(table_data=transaction_data, file_name="wallet_transactions.txt")


class SettingsScreen(Screen):
    """The screen for managing user settings and personal information."""

    def on_enter(self):
        """Called when the screen is entered."""
        super().on_enter()

        with open("data/user_data.json", "r") as file:
            json_data = file.read()

        # Load the JSON data
        self.user_data = json.loads(json_data)

        # Retrieve the stored username and password
        self.ids.first_name.text = self.user_data.get("first_name")
        self.ids.last_name.text = self.user_data.get("last_name")
        self.ids.email.text = self.user_data.get("email")
        self.ids.switch_notifications.active = self.user_data.get("switch_notifications")
        self.ids.theme_switch.active = self.user_data.get("switch_theme")


    def save_user_data(self):
        """Save the user's personal information."""
        first_name = self.ids.first_name.text
        last_name = self.ids.last_name.text
        email = self.ids.email.text

        if all((first_name, last_name, email)):
            user_name = f"{first_name}.{last_name}"

            with open("data/user_data.json", "r") as file:
                existing_data = json.load(file)

            existing_data["first_name"] = first_name
            existing_data["last_name"] = last_name
            existing_data["user_name"] = user_name
            existing_data["email"] = email

            with open("data/user_data.json", "w") as file:
                json.dump(existing_data, file)

            add_history(event_type="user_info")
            toast("Your User Data has been updated succesfully")
        else:
            show_popup(title="Error", message="Please provide all fields.", size=(500, 300))


    def save_app_settings(self):
        """Save the user's application settings."""
        switch_theme = self.ids.theme_switch.active
        switch_notifications = self.ids.switch_notifications.active

        with open("data/user_data.json", "r") as file:
            existing_data = json.load(file)

        existing_data["switch_theme"] = switch_theme
        existing_data["switch_notifications"] = switch_notifications

        with open("data/user_data.json", "w") as file:
            json.dump(existing_data, file)

        add_history(event_type="update_app")
        toast("Your App Settings have been updated succesfully")


    def show_new_password(self):
        """Called when the password icon is clicked to display the new password and change the icon."""
        self.ids.new_password.password = not self.ids.new_password.password
        self.ids.new_password_icon.icon = "eye-off" if self.ids.new_password.password else "eye"


    def show_confirm_new_password(self):
        """Called when the password icon is clicked to display the confirm password and change the icon."""
        self.ids.confirm_new_password.password = not self.ids.confirm_new_password.password
        self.ids.confirm_new_password_icon.icon = "eye-off" if self.ids.confirm_new_password.password else "eye"


    def show_old_password(self):
        """Called when the password icon is clicked to display the old password and change the icon."""
        self.ids.old_password.password = not self.ids.old_password.password
        self.ids.old_password_icon.icon = "eye-off" if self.ids.old_password.password else "eye"


    def save_password(self):
        """Save the user's new password."""
        old_password = self.ids.old_password.text
        new_password = self.ids.new_password.text
        confirm_new_password = self.ids.confirm_new_password.text

        if old_password and new_password and confirm_new_password:
            if new_password == confirm_new_password:
                if old_password == self.user_data.get("password"):
                    # Update the password in the user_data dictionary
                    self.user_data["password"] = new_password

                    # Save the updated user_data dictionary back to the JSON file
                    with open("data/user_data.json", "w") as file:
                        json.dump(self.user_data, file)

                    # Clear the password fields
                    self.ids.old_password.text = ''
                    self.ids.new_password.text = ''
                    self.ids.confirm_new_password.text = ''
                    add_history(event_type="new_password")
                    toast("Your password has been updated succesfully")
                else:
                    show_popup(title="Error", message="Your old password was incorrect")
            else:
                show_popup(title="Error", message="Passwords don't match")
        else:
            show_popup(title="Error", message="Please provide all fields.")


class WalletBubble(MDBoxLayout):
    """A widget for displaying wallet bubbles."""

    name = StringProperty('')  # The name of the wallet
    address = StringProperty('')


class LabelBubble(MDBoxLayout):
    """A widget for displaying labels."""

    text = StringProperty('') 


class LineChart(BoxLayout):
    """
    A widget for displaying a line chart.

    Args:
        data (list): The data points for the chart in the form [(x1, y1), (x2, y2), ...].
        title (str, optional): The title of the chart.

    Attributes:
        canvas (FigureCanvasKivyAgg): The canvas displaying the line chart.

    """

    def __init__(self, data, title=None, **kwargs):
        """
        Initialize the LineChart widget.

        Args:
            data (list): The data points for the chart in the form [(x1, y1), (x2, y2), ...].
            title (str, optional): The title of the chart.
            **kwargs: Additional keyword arguments to pass to the parent class.

        """
        super(LineChart, self).__init__(**kwargs)

        # Create a figure and axis for the chart
        fig, ax = plt.subplots()

        # Add the data to the chart
        x_values = [point[0] for point in data]
        y_values = [point[1] for point in data]
        ax.plot(x_values, y_values)

        # Set the title of the chart
        if title:
            ax.set_title(title)

        # Create a canvas for the chart and add it to the widget
        canvas = FigureCanvasKivyAgg(fig)
        self.add_widget(canvas)


class MyApp(MDApp):
    """
    The main application class for CoinKeeper.

    This class extends the functionality of the Kivy `App` class to create the CoinKeeper application.

    Attributes:
        screen_manager (ScreenManager): The screen manager for managing different screens in the application.
        file_manager (MDFileManager): The file manager for selecting JSON files.

    """

    def build(self):
        """
        Build the application.

        This method is called when the application is launched and is responsible for building the user interface.

        Returns:
            ScreenManager: The screen manager containing the application screens.

        """
        # Set theme settings
        self.theme_cls = ThemeManager()
        self.theme_cls.primary_palette = 'Blue'  # BlueGray
        self.theme_cls.theme_style = 'Light'
        self.theme_cls.theme_style_switch_animation = True
        self.theme_cls.theme_style_switch_animation_duration = 0.4

        # Set app title
        self.title = 'CoinKeeper'

        # Check settings
        self.check_settings()

        # Set app icon
        current_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(current_dir, 'image', 'codeblock_ico_black.png')
        self.icon = icon_path

        # Set the screen size
        Window.size = (800, 620)

        # Create screen manager and add screens
        self.screen_manager = ScreenManager(transition=FadeTransition())
        self.screen_manager.add_widget(LoginScreen(name='login'))
        self.screen_manager.add_widget(HomeScreen(name='home'))
        self.screen_manager.add_widget(NewWalletScreen(name='newWallet'))
        self.screen_manager.add_widget(CreateAccountScreen(name='create_account'))
        self.screen_manager.add_widget(WalletScreen(name='wallet'))
        self.screen_manager.add_widget(WithdrawScreen(name='Withdraw'))
        self.screen_manager.add_widget(SettingsScreen(name='settings'))
        self.screen_manager.add_widget(TransactionHistoryScreen(name='transaction_history'))
        self.screen_manager.add_widget(UserHistoryScreen(name='user_history'))

        return self.screen_manager


    def switch_theme_style(self, active):
        """
        Switch the theme style of the application.

        Args:
            active (bool): The new state of the theme switch.

        """
        # Change the theme style
        self.theme_cls.theme_style = 'Dark' if active else 'Light'
        toast("Theme change may require application restart.")


    def check_settings(self):
        """
        Check the application settings and update them accordingly.

        This method checks if there is user data and updates the settings (theme style and notifications)
        based on the existing data. If no user data is found, it sets the settings to default values.

        """
        try:
            with open("data/user_data.json", "r") as file:
                existing_data = json.load(file)

            switch_theme = existing_data["switch_theme"]
            switch_notifications = existing_data["switch_notifications"]
        except FileNotFoundError:
            # Set default values
            switch_theme = False
            switch_notifications = False

            # Save default values to file
            user_data = {
                "first_name": "",
                "last_name": "",
                "user_name": "",
                "email": "",
                "password": "",
                "switch_theme": switch_theme,
                "switch_notifications": switch_notifications,
            }

            with open("data/user_data.json", "w") as file:
                json.dump(user_data, file)

        # Change the theme style
        self.theme_cls.theme_style = 'Dark' if switch_theme else 'Light'


    def change_screen(self, screen):
        """
        Change the current screen of the application.

        Args:
            screen (str): The name of the screen to switch to.

        """
        self.screen_manager.current = screen

    def copy_to_clipboard(self, item):
        """
        Copy the specified item to the clipboard.

        Args:
            item (str): The item to be copied to the clipboard.

        """

        pyperclip.copy(item)
        toast("Copied to clipboard: " + item)


    def wallet_screen_update(self, wallet_name):
        """
        Update the wallet screen with data stored in the JSON file.

        Args:
            wallet_name (str): The name of the wallet to retrieve the information from.
        """
        # Load the JSON data from the file
        data = open_file(file_name="data/wallet_data.json", mode="r")
        wallet_info = data.get(wallet_name)

        # Set date values
        open_date = wallet_info.get('open_date')
        address = wallet_info.get('address')
        unlock_date = wallet_info.get('unlock_date')
        current_days, max_days, status = calculate_days(open_date, unlock_date)

        # Check if status is "Locked" and target value is reached
        wallet_screen = self.screen_manager.get_screen("wallet")
        target_slider = wallet_screen.ids.target_slider

        if status == "Locked" and target_slider.max <= target_slider.value:
            status = "Unlock"

        balance_usd, balance_btc = get_btc_balance(address)

        if wallet_info:
            # Set balance_value and target_value
            balance_value = balance_usd
            target_value = wallet_info.get('target_value')

            # Update wallet labels and progress bar
            wallet_screen.ids.balance_title.text = f"Current Balance: ${balance_value}"
            wallet_screen.ids.balance.text = f"${balance_value}"
            wallet_screen.ids.target.text = f"${target_value}"
            wallet_screen.ids.target_slider.max = target_value

            # Adjust progress bar value if balance exceeds target amount
            wallet_screen.ids.target_slider.value = min(balance_value, target_value)

            # Update progress bars (days left)
            wallet_screen.ids.current_days.text = f"{current_days} Days"
            wallet_screen.ids.max_days.text = f"{max_days} Days"
            wallet_screen.ids.days_slider.max = max_days

            # Adjust progress bar value if current days exceed max days
            wallet_screen.ids.days_slider.value = min(current_days, max_days)

            # Update other labels
            wallet_screen.ids.name.text = wallet_info.get("wallet_name")
            wallet_screen.ids.status.text = f"Wallet Status: {status}"
            wallet_screen.ids.unlock_date.text = f"Unlock Date: {unlock_date}"
            wallet_screen.ids.open_date.text = f"Open Date: {open_date}"

            # Get percentage for progress bar (USD/pounds)
            days_slider = wallet_screen.ids.days_slider
            if days_slider.max != days_slider.min:
                days_percentage = round((days_slider.value - days_slider.min) / (days_slider.max - days_slider.min) * 100, 1)
                wallet_screen.ids.days_percentage.text = f"{days_percentage}%"
            else:
                # Handle the case when the denominator is zero
                wallet_screen.ids.days_percentage.text = "N/A"

            # Get percentage for progress bar (days left)
            if target_slider.max != target_slider.min:
                usd_percentage = round((target_slider.value - target_slider.min) / (target_slider.max - target_slider.min) * 100, 1)
                wallet_screen.ids.usd_percentage.text = f"{usd_percentage}%"
            else:
                # Handle the case when the denominator is zero
                wallet_screen.ids.usd_percentage.text = "N/A"

        self.change_screen("wallet")


    def open_file_manager(self):
        """
        Open the file manager to select a JSON file.

        """
        documents_dir = os.path.expanduser("~\\Documents")
        manager = MDFileManager(
            exit_manager=self.exit_file_manager,
            select_path=self.select_path,
            ext=['.json']
        )
        manager.show(documents_dir)
        self.file_manager = manager

    def exit_file_manager(self, *args):
        """
        Close the file manager.

        """
        self.file_manager.close()

    def select_path(self, path):
        """
        Process the selected file path.

        Args:
            path (str): The selected file path.

        """
        wallet_info = check_file_entries(path)

        if wallet_info:
            save_wallet(wallet_info)
            add_history(event_type="new_wallet", info="Uploaded JsonFile")
            self.screen_manager.current = "home"
            self.file_manager.close()
            toast("Wallet file added succesfully")
        else:
            toast("Incorrect or missing data.")
            self.file_manager.close()


if __name__ == '__main__':
    MyApp().run()
