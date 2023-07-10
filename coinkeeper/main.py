from app_utils import *



class LoginScreen(Screen):
    def login(self, *args):
        # Retrieve username and password from the input fields
        username = self.ids.username.text
        password = self.ids.password.text

        if username and password:
            # Check if the user_data.json file exists and read its contents
            try:
                with open("data/user_data.json", "r") as file:
                    json_data = file.read()

                if json_data:
                    # Load the JSON data
                    user_data = json.loads(json_data)

                    # Retrieve the stored username and password
                    stored_username = user_data.get("user_name")
                    stored_email = user_data.get("email")
                    stored_password = user_data.get("password")

                    # Validate login credentials
                    if (username == stored_username or stored_email) and password == stored_password:
                        # Switch to the home screen if the login is successful
                        self.manager.current = "home"
                        add_history(event_type="login", info=None)
                    else:
                        # Show popup for invalid login credentials
                        show_popup(title="Login Error", message="Invalid login credentials")
                else:
                    # Show popup when user data is not found
                    show_popup(title="Login Error", message="User data not found")
            except FileNotFoundError:
                # Show popup when the user_data.json file is not found
                show_popup(title="Login Error", message="User data file not found")
        else:
            # Show popup when both username and password are not provided
            show_popup(title="Login Error", message="Please provide both username and password.", size=(500, 300))

    def forgotten_password(self):
        # Show popup when user clicks forgotten password
        show_popup(title="Forgotten Password", message="Try logging in with your email instead or request a password change.", size=(700, 500))



class CreateAccountScreen(Screen):
    def show_password(self):
        '''called when the password icon is clicked to display the password and change icon'''
        self.ids.password.password = not self.ids.password.password
        self.ids.password_icon.icon = "eye-off" if self.ids.password.password else "eye"

    def create_account(self):
        first_name = self.ids.first_name.text
        last_name = self.ids.last_name.text
        email = self.ids.email.text
        password = self.ids.password.text
        switch_theme = False
        switch_notifications = False

        if first_name and last_name and email and password:
            # Create a dictionary to hold the user data
            user_name = first_name + "." + last_name
            user_data = {
                "first_name": first_name,
                "last_name": last_name,
                "user_name": user_name,
                "email": email,
                "password": password,
                "switch_theme": switch_theme,
                "switch_notifications": switch_notifications,
            }

            # Convert the dictionary to JSON format
            json_data = json.dumps(user_data)


            # Check if the file already exists
            with open("data/user_data.json", "r") as file:
                existing_data = json.load(file)
                if existing_data["user_name"]:
                    show_popup(title="Error", message="User data already exists.", size=(500, 300))
                else:
                    # Save the JSON data to a file
                    with open("data/user_data.json", "w") as file:
                        file.write(json_data)

                    add_history(event_type="new_account", info=None)
                    self.manager.current = "home"
        else:
            show_popup(title="Error", message="Please provide all fields.", size=(500, 300))



class HomeScreen(Screen):
    def on_enter(self):
        super().on_enter()

        # Read wallet data from JSON file
        self.walletlist = self.ids['walletlist']
        data = open_file(file_name="data/wallet_data.json", type="r")
        self.update_screen(data)

    def update_screen(self, data):
        # Clear existing widgets from the wallet list
        self.walletlist.clear_widgets()

        for wallet_name, wallet_data in data.items():
            address = wallet_data.get('address', '')
            wallet_bubble = WalletBubble(name=wallet_name, address=address)
            self.walletlist.add_widget(wallet_bubble)

        # Check if there are no wallets
        if not data:
            label_bubble = LabelBubble(text="You have no wallets. Create one to view it here!")
            self.walletlist.add_widget(label_bubble)

        # Load existing JSON data from the file
        with open("data/user_history.json", "r") as file:
            existing_data = json.load(file)

        # Extract the "history" list from the existing_data dictionary
        history_data = existing_data["history"]

        column_data = [
            ("Recent User History", dp(80)),
            ("", dp(50)),
        ]

        row_data = []
        for i, event in enumerate(history_data):
            if i >= 5:  # Only add the first 5 entries
                break
            row_data.append(
                (
                    event["event"],  # Use "event" instead of "history"
                    ("history", event["date"])
                )
            )

        history_table = MDDataTable(
            column_data=column_data,
            row_data=row_data,
            elevation=2,
        )

        # Clear and add the table widget
        table = self.ids.table
        table.clear_widgets()
        table.add_widget(history_table)



class UserHistoryScreen(Screen):
    def on_enter(self):
        super().on_enter()
        # Read wallet data from JSON file
        data = open_file(file_name="data/wallet_data.json", type="r")
        self.update_screen(data)

    def update_screen(self, data):
        # Load existing JSON data from the file
        with open("data/user_history.json", "r") as file:
            existing_data = json.load(file)

        # Extract the "history" list from the existing_data dictionary
        self.history_data = existing_data["history"]

        column_data = [
            ("User History", dp(80)),
            ("", dp(50)),
        ]

        row_data = []
        for event in self.history_data:
            row_data.append(
                (
                    event["event"],  # Use "event" instead of "history"
                    ("history", event["date"])
                )
            )

        history_table = MDDataTable(
            use_pagination=True,
            column_data=column_data,
            row_data=row_data,
            elevation=2,
            check=True,
            rows_num=10,
        )

        # Clear and add the table widget
        table = self.ids.table
        table.clear_widgets()
        table.add_widget(history_table)

    def download(self):
        download_table(table_data=self.history_data, file_name="user_history.txt")


class NewWalletScreen(Screen):
    def on_enter(self):
        super().on_enter()

    def show_password(self):
        '''called when the password icon is clicked to display the passowrd and change icon'''
        self.ids.password.password = not self.ids.password.password
        self.ids.password_icon.icon = "eye-off" if self.ids.password.password else "eye"

    def on_save(self, instance, value, date_range):
        '''Events called when the "OK" dialog box button is clicked.'''
        self.ids.date_of_completion.text = str(value)

    def on_cancel(self, instance, value):
        '''Events called when the "CANCEL" dialog box button is clicked.'''
        self.ids.date_of_completion.text = str(value)

    def show_date_picker(self):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_save, on_cancel=self.on_cancel)
        date_dialog.open()

    def create_wallet(self):
        wallet_name = self.ids.wallet_name.text
        unlock_date = self.ids.date_of_completion.text
        target_amount = self.ids.target_amount.text
        password = self.ids.password.text
        target_amount = float(target_amount)
        today = date.today()
        open_date = today.strftime("%Y-%m-%d")

        encrypted_private_key, public_key, address = create_BTC_keys(password)

        wallet_info = {
            "wallet_name": wallet_name,
            "open_date": open_date,
            "unlock_date": unlock_date,
            "target_amount": target_amount,
            "password": password,
            "public_key": public_key,
            "encrypted_private_key": encrypted_private_key,
            "address": address,
        }

        # Perform validation and wallet creation logic here
        if self.check(wallet_info):
            if unlock_date != open_date and target_amount != 0.0:
                # Define the confirmed function
                def confirmed(dialog_instance):
                    dialog_instance.dismiss()
                    save_wallet(wallet_info)
                    self.clear()
                    add_history(event_type="new_wallet", info=wallet_name)
                    self.manager.current = "home"

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


    def check(self, wallet_info):

        data = open_file(file_name="data/wallet_data.json", type="r")

        if any(value == "" for value in wallet_info.values()):
            show_popup(title="Error", message="Please provide all fields.", size=(500, 300))
            return False

        elif wallet_info["wallet_name"] in data:
            show_popup(title="Error", message="Wallet name already in use")
            return False

        return True

    def clear(self):
        self.ids.wallet_name.text = ""
        self.ids.date_of_completion.text = ""
        self.ids.target_amount.text = ""
        self.ids.password.text = ""


    def help(self):
        show_popup(
            title="Help",
            message="Please provide the following information:\n\n"
                    "- Wallet Name: The name of the wallet you want to create.\n\n"
                    "- Unlock Date: The date by which you plan to reach your target.\n\n"
                    "- Target Amount: The desired amount of funds you aim to\n accumulate in the wallet.\n\n"
                    "- Password: The password used to encrypt the private key.\n It will NOT be shown again\n\n"
                    "-IMPORTANT: The wallet will only become accessible once the\n ""Unlock Date"" or the ""target amount"" has been reached. \n\n",
            size=(700, 700)
        )



class WalletScreen(Screen):
    def on_enter(self):
        super().on_enter()

        # Load the JSON data from the file
        data = open_file(file_name="data/wallet_data.json", type="r")
        self.wallet_info = data.get(self.ids.name.text)

        # Set values
        self.address = self.wallet_info.get('address')
        self.target_amount = self.wallet_info.get('target_amount')
        self.balance_usd, self.balance_btc = get_btc_balance(self.address)

        # Prepare the transaction data for the line chart
        transactions = get_transaction_history(self.address)
        if transactions is None:
            data = []
        else:
            data = []
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

        switch_currency = self.ids.switch_currency.active

        if switch_currency:
            self.ids.balance_title.text = f"Current Balance: {self.balance_btc}"
        else:
            self.ids.balance_title.text = f"Current Balance: ${self.balance_usd}"


    def delete(self, wallet_name):
        if self.ids.balance.text == "$0.0":
            def delete_action(dialog_instance):
                dialog_instance.dismiss()  # Close the popup dialog
                data = open_file(file_name="data/wallet_data.json", type="r")
                wallet_info = data.get(wallet_name)
                del data[wallet_name]
                save_file(file_name="data/wallet_data.json", data=data)
                self.manager.current = "home"
                add_history(event_type="del_wallet", info=wallet_name)

            confirm_popup(title="Confirm Deletion", message="Are you sure you want to delete the wallet?", action=delete_action)
        else:
            show_popup(title="Error", message="This Wallet is not empty!", size=(500, 300))


    def Withdraw(self):
        if self.ids.status.text == "Wallet Status: Locked":
            show_popup(title="Withdraw", message="This Wallet is currently locked", size=(500, 300))
        else:
            self.manager.current ="Withdraw"

    def deposit(self):
        show_popup(title="Deposit", message=self.address, size=(500, 300), button_on=False)


    def download(self):
        # Load the JSON data from the file
        data = open_file(file_name="data/wallet_data.json", type="r")

        # Find the entry connected to self.ids.status.text
        entry_data = data.get(self.ids.name.text)

        # Create a file for the selected entry
        file_name = f"{self.ids.name.text}_wallet_data.json"
        file_path = os.path.join(os.path.expanduser("~"), "Downloads", file_name)

        # Save the entry data to the file
        with open(file_path, "w") as output_file:
            json.dump(entry_data, output_file)

        # Show a popup message indicating successful download
        show_popup(title="Download", message=f"Exported data to: {file_path}", size=(500, 300), button_on=False)



class WithdrawScreen(Screen):
    def on_enter(self):
        super().on_enter()

        # Access the name value from the WalletScreen
        wallet_screen = self.manager.get_screen('wallet')
        name_value = wallet_screen.ids.name.text

        # Load the JSON data from the file
        data = open_file(file_name="data/wallet_data.json", type="r")
        self.wallet_info = data.get(name_value)

        # Set values
        self.address = self.wallet_info.get('address')
        self.encrypted_private_key = self.wallet_info.get('encrypted_private_key')
        self.balance_usd, self.balance_btc = get_btc_balance(self.address)

        # Schedule the interval to update values every 60 seconds
        self.update_values()  # Initial call with the current TextInput instance


    def update_values(self):
        self.amount = self.ids.amount.text
        self.btc_fee, self.usd_fee = send_transaction(send_to=None, from_address=None, amount=self.amount)
        self.gross_cost = self.usd_fee + self.balance_usd

        # Update values
        self.ids.balance_title.text = f"Available Balance: ${self.balance_usd}"
        self.ids.fee.text = f"Sending Fee: ${self.usd_fee}"
        self.ids.gross_cost.text = f"Net Cost: ${self.gross_cost}"
        self.ids.amount.icon_right = "currency-usd"


    def cancel(self):
        self.clear()
        self.manager.current ="wallet"


    def send(self):
        amount = self.ids.amount.text
        password = self.ids.password.text
        address = self.ids.address.text

        if amount and password and address:
            if float(amount) < self.balance_usd and float(amount) != 0:
                if is_valid_btc_address(address):
                    dec_private_key = decrypt(self.encrypted_private_key, password)
                    if dec_private_key:
                        if send_transaction(send_to=address, from_address=dec_private_key, amount=amount):
                            show_popup(title="Send/Withdraw", message=dec_private_key, size=(500, 300))
                        else:
                            show_popup(title="Error", message="Unable to send", size=(500, 300))
                    else:
                        show_popup(title="Error", message="Incorrect password", size=(500, 300))
                else:
                    show_popup(title="Error", message="Invalid Bitcoin address", size=(500, 300))
            else:
                show_popup(title="Error", message="Insufficient funds", size=(500, 300))
        else:
            show_popup(title="Error", message="Please provide all fields.", size=(500, 300))


    def help(self):
        message = "To send a transaction, fill in the following fields:\n\n"
        message += "- Amount: Enter the amount of Bitcoin you want to send.\n"
        message += "- Password: Provide your password to decrypt the private key.\n"
        message += "- Address: Specify the recipient's Bitcoin address.\n\n"
        message += "Once you have filled in all the fields, click the 'Send' button to proceed with the transaction.\n"
        message += "Please make sure to double-check the recipient's address before sending.\n\n"
        message += "If you encounter any issues or errors, please refer to the error messages displayed or contact our support team for assistance."
        show_popup(title="Help", message=message, size=(500, 300))


    def change_currency(self):
        if self.ids.balance_title.text == f"Avalable Balance: ${self.balance_usd}":
            self.ids.balance_title.text = f"Avalable Balance: {self.balance_btc}"
            self.ids.fee.text = f"Sending Fee: {self.btc_fee}"
            self.gross_cost = self.btc_fee + self.balance_btc
            self.ids.gross_cost.text = f"Net Cost: {self.gross_cost}"
            self.ids.amount.icon_right = "currency-btc"
        else:
            self.ids.balance_title.text = f"Avalable Balance: ${self.balance_usd}"
            self.ids.amount.icon_right = "currency-usd"
            self.ids.fee.text = f"Sending Fee: ${self.usd_fee}"
            self.gross_cost = self.usd_fee + self.balance_usd
            self.ids.gross_cost.text = f"Net Cost: ${self.gross_cost}"


    def set_amount(self, value):
        if self.balance_usd > 0.0:
            self.ids.amount.text = self.balance_usd/value


    def clear(self):
        self.ids.amount.text = ""
        self.ids.password.text = ""
        self.ids.address.text = ""



class TransactionHistoryScreen(Screen):
    def on_pre_enter(self):
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
        transaction_data = get_transaction_history(self.address)

        download_table(table_data=transaction_data, file_name="wallet_transactions.txt")



class SettingsScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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
            show_popup(title="Success", message="Your User Data has been updated")
        else:
            show_popup(title="Error", message="Please provide all fields.", size=(500, 300))


    def save_app_settings(self):
        switch_theme = self.ids.theme_switch.active
        switch_notifications = self.ids.switch_notifications.active

        with open("data/user_data.json", "r") as file:
            existing_data = json.load(file)

        existing_data["switch_theme"] = switch_theme
        existing_data["switch_notifications"] = switch_notifications

        with open("data/user_data.json", "w") as file:
            json.dump(existing_data, file)

        add_history(event_type="update_app")
        show_popup(title="Success", message="Your App Settings have been updated")


    def show_new_password(self):
        '''called when the password icon is clicked to display the passowrd and change icon'''
        self.ids.new_password.password = not self.ids.new_password.password
        self.ids.new_password_icon.icon = "eye-off" if self.ids.new_password.password else "eye"

    def show_old_password(self):
        '''called when the password icon is clicked to display the passowrd and change icon'''
        self.ids.old_password.password = not self.ids.old_password.password
        self.ids.old_password_icon.icon = "eye-off" if self.ids.old_password.password else "eye"


    def save_password(self):
        if self.ids.old_password.text == self.user_data.get("password") and self.ids.old_password.text != '':

            # Update the password in the user_data dictionary
            self.user_data["password"] = self.ids.new_password.text

            # Save the updated user_data dictionary back to the JSON file
            with open("data/user_data.json", "w") as file:
                json.dump(self.user_data, file)

            # Clear the password fields
            self.ids.old_password.text = ''
            self.ids.new_password.text = ''
            add_history(event_type="new_password")
            show_popup(title="Success", message="Your password has been updated")
        else:
            show_popup(title="Error", message="Your old password was incorrect")



class WalletBubble(MDBoxLayout):
    '''A widget for the wallet bubbles'''
    name = StringProperty('')
    address = StringProperty('')


class LabelBubble(MDBoxLayout):
    '''A widget for displaying labels'''
    text = StringProperty('')


class LineChart(BoxLayout):
    def __init__(self, data, title=None, **kwargs):
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
    def build(self):
        # Set theme settings
        self.theme_cls.primary_palette = 'Blue'
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

        # Bind check_connection() method to the 'on_touch_down' event of the screen manager
        self.screen_manager.bind(on_touch_down=self.check_connection)

        return self.screen_manager

    def check_connection(self, instance, touch):
        """Check internet connection and show popup if not available."""
        if not check_internet_connection():
            show_popup("No Internet Connection", "Please check your internet connection.")
            self.screen_manager.current = 'login'

            Clock.schedule_once(self.wait_for_connection, 1)

    def wait_for_connection(self, dt):
        """Wait for internet connection before continuing."""
        while not check_internet_connection():
            Clock.tick()


    def switch_theme_style(self, active):
        if active:
            self.theme_cls.theme_style = 'Dark'
        else:
            self.theme_cls.theme_style = 'Light'

    def change_screen(self, screen):
        self.screen_manager.current = screen

    def copy_to_clipboard(self, item):
        clipboard.copy(item)
        show_popup(title="Copyed to clipboard", message=item)


    def check_settings(self):
        """ checks if there is user data and updates the setting accordingly, if no user data it sets the settings to default values"""
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

        if switch_theme:
            self.theme_cls.theme_style = 'Dark'
        else:
            self.theme_cls.theme_style = 'Light'


    def wallet_screen_update(self, wallet_name):
        """
        Takes one argument `wallet_name` which indicates where to look for the needed
        information and updates the wallet screen with data stored in the JSON file.
        """
        # Load the JSON data from the file
        data = open_file(file_name="data/wallet_data.json", type="r")
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

            # set balance_value and target_amount
            balance_value = float(balance_usd)
            target_amount = float(wallet_info.get('target_amount'))

            # Update wallet labels and progress bar
            wallet_screen.ids.balance_title.text = f"Current Balance: ${balance_value}"

            wallet_screen.ids.balance.text = f"${balance_value}"
            wallet_screen.ids.target.text = f"${target_amount}"
            wallet_screen.ids.target_slider.max = target_amount

            # Adjust progress bar value if balance exceeds target amount
            wallet_screen.ids.target_slider.value = min(balance_value, target_amount)

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
        documents_dir = os.path.join(os.path.expanduser("~"), "Documents")
        manager = MDFileManager(
            exit_manager=self.exit_file_manager,
            select_path=self.select_path,
            ext=['.json']
        )
        manager.show(documents_dir)  # Show the file manager starting from the documents directory
        self.file_manager = manager  # Store the file manager instance


    def exit_file_manager(self, *args):
        self.file_manager.close()  # Close the file manager

    def select_path(self, path):
        wallet_info = check_file_entries(path)

        if wallet_info:
            save_wallet(wallet_info)
            add_history(event_type="new_wallet", info="Uploaded JsonFile")
            self.screen_manager.current = "home"
            self.file_manager.close()

        else:
            show_popup(title="Error", message="Incorrect or missing data")
            self.file_manager.close()


if __name__ == '__main__':
    MyApp().run()
