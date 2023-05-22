import requests

class BitcoinWallet:
    def __init__(self, balance):
        self.balance = balance

    def add_bitcoin(self, amount):
        self.balance += amount

    def remove_bitcoin(self, amount):
        if self.balance >= amount:
            self.balance -= amount
        else:
            print("Insufficient Bitcoin balance to sell.")

class User:
    def __init__(self, name, balance):
        self.name = name
        self.balance = balance
        self.bitcoin_wallet = BitcoinWallet(0)

    def buy_bitcoin(self, amount):
        response = requests.get("https://api.coindesk.com/v1/bpi/currentprice/BTC.json")
        if response.status_code == 200:
            data = response.json()
            exchange_rate = data["bpi"]["USD"]["rate_float"]
            total_cost = amount * exchange_rate

            if self.balance >= total_cost:
                self.balance -= total_cost
                self.bitcoin_wallet.add_bitcoin(amount)
                print(f"Successfully bought {amount} Bitcoin at the exchange rate of {exchange_rate}.")
            else:
                print("Insufficient balance to buy Bitcoin.")
        else:
            print("Failed to fetch Bitcoin exchange rate.")

    def sell_bitcoin(self, amount):
        response = requests.get("https://api.coindesk.com/v1/bpi/currentprice/BTC.json")
        if response.status_code == 200:
            data = response.json()
            exchange_rate = data["bpi"]["USD"]["rate_float"]
            total_earning = amount * exchange_rate

            if self.bitcoin_wallet.balance >= amount:
                self.bitcoin_wallet.remove_bitcoin(amount)
                self.balance += total_earning
                print(f"Successfully sold {amount} Bitcoin at the exchange rate of {exchange_rate}.")
            else:
                print("Insufficient Bitcoin balance to sell.")
        else:
            print("Failed to fetch Bitcoin exchange rate.")

# Usage
user = User("John", 10000)

user.buy_bitcoin(0.2)  # John buys 0.2 Bitcoin
user.sell_bitcoin(0.1)  # John sells 0.1 Bitcoin