import secrets
import hashlib

class Accounts:
    dB = "vault_data"
    security_infrastructure = SecurityInfrastructure(encryption_key)

    def __init__(self, id: int, name: str, balance: float, user_id: int, trader):
        self.id = id
        self.name = name
        self.balance = Decimal(str(balance))
        self.user_id = user_id
        self.user_list = []
        self.crypto_wallet = CryptoWallet()
        self.trader = trader

    @classmethod
    def buy_crypto(cls, name, balance, trader, currency, amount, account_id):
        exchange_rate = trader.get_exchange_rate(API_key, currency, 'USD')
        total_cost = amount * exchange_rate

        if balance >= total_cost:
            balance -= total_cost
            account_id = int(account_id)
            CryptoWallet.add_currency(currency, amount, account_id)
            print(f"Successfully bought {amount} {currency} at the exchange rate of {exchange_rate}.")
        else:
            print("Insufficient balance to buy cryptocurrency.")

    @classmethod
    def sell_crypto(cls, name, balance, trader, currency, amount):
        exchange_rate = trader.get_exchange_rate(currency, 'USD')
        total_earning = amount * exchange_rate

        if CryptoWallet.get_balance(currency) >= amount:
            CryptoWallet.remove_currency(currency, amount)
            balance += total_earning
            print(f"Successfully sold {amount} {currency} at the exchange rate of {exchange_rate}.")
        else:
            print("Insufficient cryptocurrency balance to sell.")

    def transfer(self, recipient: Union['Accounts', 'AnonymousAccounts'], amount: float):
        # Check if amount is positive.
        if amount <= 0:
            raise ValueError("Amount must be positive")
        # Check if the sender has enough balance.
        if self.balance < Decimal(str(amount)):
            raise ValueError("Insufficient balance")

        # Deduct the amount from the sender's balance.
        self.balance -= Decimal(str(amount))
        # Add the amount to the recipient's balance.
        recipient.balance += Decimal(str(amount))

        # Create a transaction.
        transaction = Transaction(
            sender=self.id,
            receiver=recipient.id,
            amount=Decimal(str(amount)),
        )
        # Add the transaction to the blockchain.
        Blockchain.add_transaction(transaction)

    def get_balance(self) -> float:
        query = """
            SELECT balance FROM accounts WHERE id = %(id)s;
        """
        results = MySQLConnection(Accounts.dB).query_db(query, {"id": self.id})
        if len(results) == 0:
            raise ValueError(f"No account found with id {self.id}")
        return float(results[0]["balance"])

    @classmethod
    def get_all(cls, trader) -> List['Accounts']:
        query = """
            SELECT accounts.*, users.first_name, users.last_name, users.email FROM accounts 
            LEFT JOIN users ON accounts.user_id = users.id;
        """
        results = MySQLConnection(cls.dB).query_db(query)

        if results:
            accounts = []
            for result in results:
                user_data = {
                    "id": result["user_id"],
                    "first_name": result["first_name"],
                    "last_name": result["last_name"],
                    "email": result["email"],
                    "password": None,
                }
                user_info = User(user_data)
                account = cls(result["id"], result["name"], result["balance"], result["user_id"], trader)
                account.user_list.append(user_info)
                accounts.append(account)
            return accounts

        return None

    @classmethod
    def get_by_name(cls, name: str) -> 'Accounts':
        query = """
            SELECT * FROM accounts WHERE name = %(name)s;
        """
        results = MySQLConnection(cls.dB).query_db(query, {"name": name})
        if len(results) == 0:
            raise ValueError(f"No account found with name {name}")
        return cls(results[0]["id"], results[0]["name"], results[0]["balance"], results[0]["user_id"])

    @classmethod
    def create(cls, name: str, balance: float, user_id: Optional[int] = None, trader: str = "") -> 'Accounts':
        if not user_id:
            user_id = session.get('user_id')
        if not user_id:
            raise ValueError("No user ID provided")

        # create account with given name and balance for specified user
        query = """
            INSERT INTO accounts (name, balance, user_id, trader)
            VALUES (%(name)s, %(balance)s, %(user_id)s, %(trader)s);
        """
        MySQLConnection(Accounts.dB).query_db(query, {"name": name, "balance": balance, "user_id": user_id, "trader": trader})

        # retrieve newly created account from database
        query = """
            SELECT * FROM accounts WHERE name = %(name)s AND balance = %(balance)s AND user_id = %(user_id)s;
        """
        result = MySQLConnection(Accounts.dB).query_db(query, {"name": name, "balance": balance, "user_id": user_id})

        # return new Accounts instance with retrieved data
        return cls(result[0]["id"], result[0]["name"], result[0]["balance"], result[0]["user_id"], trader)

    @classmethod
    def get_by_user_id(cls, user_id: int, trader: str) -> 'Accounts':
        query = """
            SELECT * FROM accounts WHERE id = %(user_id)s;
        """
        results = MySQLConnection(cls.dB).query_db(query, {"user_id": user_id})
        if len(results) == 0:
            raise ValueError(f"No account found with user ID {user_id}")
        return cls(results[0]["id"], results[0]["name"], results[0]["balance"], results[0]["user_id"], trader)


class AnonymousAccounts(Accounts):
    def __init__(self, id: int, name: str, balance: float, trader):
        super().__init__(id, name, balance, None, trader)

    @classmethod
    def create(cls, name: str, balance: float, trader: str = "") -> 'AnonymousAccounts':
        # Generate a random identifier for the anonymous account
        anonymous_id = secrets.token_hex(16)

        # Encrypt the anonymous identifier for stronger anonymity
        encrypted_id = hashlib.sha256(anonymous_id.encode()).hexdigest()

        # create account with given name and balance
        query = """
            INSERT INTO accounts (name, balance, trader, anonymous_id)
            VALUES (%(name)s, %(balance)s, %(trader)s, %(anonymous_id)s);
        """
        MySQLConnection(Accounts.dB).query_db(query, {"name": name, "balance": balance, "trader": trader, "anonymous_id": encrypted_id})

        # retrieve newly created account from database
        query = """
            SELECT * FROM accounts WHERE anonymous_id = %(anonymous_id)s;
        """
        result = MySQLConnection(Accounts.dB).query_db(query, {"anonymous_id": encrypted_id})

        # return new AnonymousAccounts instance with retrieved data
        return cls(result[0]["id"], result[0]["name"], result[0]["balance"], trader)