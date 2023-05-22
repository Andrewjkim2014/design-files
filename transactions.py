import requests

class User:
    def __init__(self, name, balance, bitcoin_balance):
        self.name = name
        self.balance = balance
        self.bitcoin_balance = bitcoin_balance

    def buy_bitcoin(self, amount):
        bitcoin_price = self.get_bitcoin_price()
        total_cost = amount * bitcoin_price

        if self.balance >= total_cost:
            self.balance -= total_cost
            self.bitcoin_balance += amount
            print(f"{self.name} successfully bought {amount} Bitcoin at the price of {bitcoin_price}.")
        else:
            print(f"{self.name} has insufficient balance to buy Bitcoin.")

    def sell_bitcoin(self, amount):
        bitcoin_price = self.get_bitcoin_price()
        total_earning = amount * bitcoin_price

        if self.bitcoin_balance >= amount:
            self.bitcoin_balance -= amount
            self.balance += total_earning
            print(f"{self.name} successfully sold {amount} Bitcoin at the price of {bitcoin_price}.")
        else:
            print(f"{self.name} has insufficient Bitcoin balance to sell.")

    def get_bitcoin_price(self):
        # Make a request to the Bitcoin API to get the current price
        response = requests.get("https://api.bitcoin.com/v1/ticker")
        if response.status_code == 200:
            data = response.json()
            return data['price']
        else:
            print("Failed to fetch Bitcoin price.")
            return None

# Usage
user = User("John", 10000, 0.5)
user.buy_bitcoin(0.2)  # John buys 0.2 Bitcoin
user.sell_bitcoin(0.1)  # John sells 0.1 Bitcoin