import secrets
import hashlib

# ... existing imports ...

# Generate a secret key for encrypting sensitive data
secret_key = secrets.token_hex(16)

@app.route('/accounts', methods=['GET'])
def get_all_accounts():
    # ... existing code ...

@app.route('/accounts/<int:account_id>', methods=['GET'])
def get_account_by_id(account_id):
    # ... existing code ...

@app.route('/accounts', methods=['POST'])
def create_account():
    name = request.form['name']
    balance = request.form['balance']
    user_id = session.get('user_id')

    try:
        trader = CryptoTrader(API_key)
        encrypted_name = hashlib.sha256(name.encode() + secret_key.encode()).hexdigest()
        encrypted_balance = hashlib.sha256(balance.encode() + secret_key.encode()).hexdigest()
        Accounts.create(encrypted_name, encrypted_balance, user_id, str(trader))
        return redirect("/accounts")
    except ValueError as e:
        return render_template('crypto_wallets.html', message=str(e)), 400

@app.route('/accounts/<int:account_id>/transfer', methods=['POST'])
def transfer_amount(account_id):
    data = request.get_json()
    recipient_id = request.form['recipient_id']
    amount = request.form['amount']

    try:
        sender = Accounts.get_by_id(account_id)
        recipient = Accounts.get_by_id(recipient_id)
        sender.transfer(recipient, amount)
        return render_template('crypto_wallets.html', message='Transfer successful'), 200
    except ValueError as e:
        return render_template('crypto_wallets.html', message=str(e)), 400

@app.route('/accounts/buy_crypto', methods=['POST'])
def buy_crypto():
    # ... existing code ...

@app.route('/accounts/<int:account_id>/sell_crypto', methods=['POST'])
def sell_crypto(account_id):
    data = request.get_json()
    currency = request.form['currency']
    amount = request.form['amount']

    try:
        account = Accounts.get_by_id(account_id)
        balance = account.get_balance()
        Accounts.sell_crypto(account.name, balance, trader, currency, amount)
        return render_template('crypto_wallets.html', message='Cryptocurrency sold successfully'), 200
    except ValueError as e:
        return render_template('crypto_wallets.html', message=str(e)), 400