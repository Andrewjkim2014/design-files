class WalletTransaction:
    @classmethod
    def deposit(cls, currency: str, amount: float):
        # Perform validation checks, if necessary
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        # Perform deposit operation
        wallet = CryptoWallet.from_database()
        wallet.add_currency(currency, amount)
        
        # Update the wallet data in the database
        cls.update_wallet_data(wallet)

    @staticmethod
    def update_wallet_data(wallet: CryptoWallet):
        # Update the wallet data in the database
        query = """
            TRUNCATE TABLE crypto_wallet;
        """
        MySQLConnection('your_database_name').query_db(query)

        for currency, amount in wallet.wallet_data.items():
            query = """
                INSERT INTO crypto_wallet (currency, amount) VALUES (%s, %s);
            """
            MySQLConnection('your_database_name').query_db(query, (currency, amount))