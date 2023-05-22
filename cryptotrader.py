class CryptoTrader:
    def __init__(self, exchange_rate_api_key):
        self.exchange_rate_api_key = exchange_rate_api_key
        self.crypto_wallet = CryptoWallet()
        self.blockchain_platform = BlockchainPlatform()

    def get_exchange_rate(self, currency_from, currency_to):
        url = f"https://api.example.com/exchangerates?from={currency_from}&to={currency_to}&api_key={self.exchange_rate_api_key}"

        try:
            response = requests.get(url)
            data = response.json()
            exchange_rate = data['rate']
            return exchange_rate
        except requests.exceptions.RequestException as e:
            print(f"Error occurred while fetching exchange rate: {e}")
            return None

    def buy_crypto(self, user, currency, amount):
        exchange_rate = self.get_exchange_rate(currency, 'USD')
        cost = amount * exchange_rate

        # Deduct the cost from the user's account
        user.deduct_funds(cost)

        # Execute a buy order on the blockchain platform
        transaction_id = self.blockchain_platform.execute_buy_order(user, currency, amount)

        if transaction_id:
            # Store the purchased cryptocurrency in the user's crypto wallet
            self.crypto_wallet.add_crypto(user, currency, amount)

    def sell_crypto(self, user, currency, amount):
        exchange_rate = self.get_exchange_rate(currency, 'USD')
        earnings = amount * exchange_rate

        # Remove the sold cryptocurrency from the user's crypto wallet
        self.crypto_wallet.remove_crypto(user, currency, amount)

        # Execute a sell order on the blockchain platform
        transaction_id = self.blockchain_platform.execute_sell_order(user, currency, amount)

        if transaction_id:
            # Add the earnings to the user's account
            user.add_funds(earnings)