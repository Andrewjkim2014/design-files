import bcrypt
from cryptography.fernet import Fernet
import base64

# Secret key for encryption
secret_key = b'your-secret-key'  # Replace with your secret key
cipher_suite = Fernet(base64.urlsafe_b64encode(secret_key))

class User:
    # ... existing code ...

    def __init__(self, data):
        self.id = data["id"]
        self.first_name = data["first_name"]
        self.last_name = data["last_name"]
        self.email = cipher_suite.decrypt(data["encrypted_email"].encode()).decode()
        self.password = data["password"]

    @classmethod
    def signup(cls, first_name: str, last_name: str, email: str, password: str) -> None:
        # Encrypt the email with the secret key
        encrypted_email = cipher_suite.encrypt(email.encode()).decode()

        query = """
            INSERT INTO users (first_name, last_name, encrypted_email, password)
            VALUES (%(first_name)s, %(last_name)s, %(encrypted_email)s, %(password)s);
        """
        result = MySQLConnection(User.dB).query_db(query, {
            "first_name": first_name,
            "last_name": last_name,
            "encrypted_email": encrypted_email,
            "password": password
        })
        print("Signup successful")

    @classmethod
    def login(cls, email: str, password: str) -> 'User':
        query = """
            SELECT * FROM users WHERE encrypted_email = %(encrypted_email)s;
        """
        encrypted_email = cipher_suite.encrypt(email.encode()).decode()

        result = MySQLConnection(User.dB).query_db(query, {
            "encrypted_email": encrypted_email,
        })
        if len(result) == 0:
            raise ValueError("Invalid credentials")

        stored_password = result[0]["password"].encode()

        if not bcrypt.checkpw(password.encode(), stored_password):
            raise ValueError("Invalid credentials")

        # ... existing code ...




        import bcrypt
from cryptography.fernet import Fernet
import base64

# Secret key for encryption
secret_key = b'your-secret-key'  # Replace with your secret key
cipher_suite = Fernet(base64.urlsafe_b64encode(secret_key))

class User:
    # ... existing code ...

    @classmethod
    def signup(cls, first_name: str, last_name: str, email: str, password: str) -> None:
        # Generate a salt with specified rounds (default value is 12)
        salt = bcrypt.gensalt(rounds=10)

        # Hash the password with the salt
        hashed_password = bcrypt.hashpw(password.encode(), salt)

        query = """
            INSERT INTO users (first_name, last_name, email, password, salt)
            VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password)s, %(salt)s);
        """
        result = MySQLConnection(User.dB).query_db(query, {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "password": hashed_password.decode(),  # Store the hashed password as a string
            "salt": salt.decode()  # Store the salt as a string
        })
        print("Signup successful")

    @classmethod
    def login(cls, email: str, password: str) -> 'User':
        query = """
            SELECT * FROM users WHERE email = %(email)s;
        """
        result = MySQLConnection(User.dB).query_db(query, {"email": email})
        if len(result) == 0:
            raise ValueError("Invalid credentials")

        stored_password = result[0]["password"].encode()
        salt = result[0]["salt"].encode()

        if not bcrypt.checkpw(password.encode(), stored_password):
            raise ValueError("Invalid credentials")

        # ... existing code ...




        import bcrypt
from cryptography.fernet import Fernet
import base64
import random
import string

# Secret key for encryption
secret_key = b'your-secret-key'  # Replace with your secret key
cipher_suite = Fernet(base64.urlsafe_b64encode(secret_key))

class User:
    # ... existing code ...

    @classmethod
    def signup(cls, first_name: str, last_name: str, email: str, password: str) -> None:
        # Generate a salt with specified rounds (default value is 12)
        salt = bcrypt.gensalt(rounds=10)

        # Hash the password with the salt
        hashed_password = bcrypt.hashpw(password.encode(), salt)

        # Generate anonymous factor for email
        anonymous_factor = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        encrypted_email = cipher_suite.encrypt((email + anonymous_factor).encode()).decode()

        query = """
            INSERT INTO users (first_name, last_name, encrypted_email, password, salt)
            VALUES (%(first_name)s, %(last_name)s, %(encrypted_email)s, %(password)s, %(salt)s);
        """
        result = MySQLConnection(User.dB).query_db(query, {
            "first_name": first_name,
            "last_name": last_name,
            "encrypted_email": encrypted_email,
            "password": hashed_password.decode(),  # Store the hashed password as a string
            "salt": salt.decode()  # Store the salt as a string
        })
        print("Signup successful")

    @classmethod
    def login(cls, email: str, password: str) -> 'User':
        query = """
            SELECT * FROM users WHERE encrypted_email = %(encrypted_email)s;
        """
        anonymous_factor = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        encrypted_email = cipher_suite.encrypt((email + anonymous_factor).encode()).decode()

        result = MySQLConnection(User.dB).query_db(query, {
            "encrypted_email": encrypted_email
        })
        if len(result) == 0:
            raise ValueError("Invalid credentials")

        stored_password = result[0]["password"].encode()
        salt = result[0]["salt"].encode()

        if not bcrypt.checkpw(password.encode(), stored_password):
            raise ValueError("Invalid credentials")



import bcrypt
from cryptography.fernet import Fernet
import base64
import random
import string

# Secret key for encryption
secret_key = b'your-secret-key'  # Replace with your secret key
cipher_suite = Fernet(base64.urlsafe_b64encode(secret_key))

class User:
    # ... existing code ...

    @classmethod
    def signup(cls, first_name: str, last_name: str, email: str, password: str) -> None:
        # Generate a salt with specified rounds (default value is 12)
        salt = bcrypt.gensalt(rounds=10)

        # Hash the password with the salt
        hashed_password = bcrypt.hashpw(password.encode(), salt)

        anonymous_factor = ''
        unique_anonymous_factor = False
        while not unique_anonymous_factor:
            # Generate anonymous factor for email
            anonymous_factor = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            encrypted_email = cipher_suite.encrypt((email + anonymous_factor).encode()).decode()

            # Check if encrypted email with anonymous factor already exists in the database
            query = """
                SELECT COUNT(*) as count FROM users WHERE encrypted_email = %(encrypted_email)s;
            """
            result = MySQLConnection(User.dB).query_db(query, {
                "encrypted_email": encrypted_email
            })
            count = result[0]['count']
            if count == 0:
                unique_anonymous_factor = True

        query = """
            INSERT INTO users (first_name, last_name, encrypted_email, password, salt)
            VALUES (%(first_name)s, %(last_name)s, %(encrypted_email)s, %(password)s, %(salt)s);
        """
        result = MySQLConnection(User.dB).query_db(query, {
            "first_name": first_name,
            "last_name": last_name,
            "encrypted_email": encrypted_email,
            "password": hashed_password.decode(),  # Store the hashed password as a string
            "salt": salt.decode()  # Store the salt as a string
        })
        print("Signup successful")

    @classmethod
    def login(cls, email: str, password: str) -> 'User':
        query = """
            SELECT * FROM users WHERE encrypted_email = %(encrypted_email)s;
        """

        anonymous_factor = ''
        unique_anonymous_factor = False
        while not unique_anonymous_factor:
            # Generate anonymous factor for email
            anonymous_factor = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            encrypted_email = cipher_suite.encrypt((email + anonymous_factor).encode()).decode()

            # Check if encrypted email with anonymous factor exists in the database
            result = MySQLConnection(User.dB).query_db(query, {
                "encrypted_email": encrypted_email
            })
            if len(result) == 0:
                unique_anonymous_factor = True

        result = MySQLConnection(User.dB).query_db(query, {
            "encrypted_email": encrypted_email
        })
        if len(result) == 0:
            raise ValueError("Invalid credentials")

        stored_password = result[0]["password"].encode()
        salt = result[0]["salt"].encode()

        if not bcrypt.checkpw(password.encode(), stored_password):
            raise ValueError("Invalid credentials")

        # ... existing code ...
