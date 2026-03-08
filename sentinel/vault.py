import sqlite3
import os
from cryptography.fernet import Fernet
from datetime import datetime


# Database path
DB_PATH = "secrets.db"
KEY_FILE = "vault.key"

# Function to initialize Vault: Generate Fernet key and set up SQLite database
def init_vault():
    # 1. Create Fernet encryption key only if it doesn't exist
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, 'wb') as key_file:
            key_file.write(key)
        print("Encryption key generated and saved to vault.key")
    # 3. Set up SQLite database to store secrets
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create a table to store secrets (if it doesn't exist)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS secrets (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            encrypted_value BLOB NOT NULL
        )
    ''')

    # Commit changes and close the connection
    conn.commit()
    conn.close()
    print("SQLite database initialized: secrets.db")

# Function to store secret (encrypt it and save to the database)
def store_secret(secret_name: str, secret_value: str):
    # Load the Fernet key from the vault.key file
    with open(KEY_FILE, 'rb') as key_file:
        key = key_file.read()

    # Create a Fernet cipher object using the loaded key
    cipher = Fernet(key)

    # Connect to the SQLite database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check if the secret already exists in the database
    cursor.execute('SELECT id FROM secrets WHERE name = ?', (secret_name,))
    if cursor.fetchone():
        conn.close()
        return f"op://vault/sentinelai/{secret_name.lower().replace(' ', '-')}"
    
    # Encrypt the secret value
    encrypted_value = cipher.encrypt(secret_value.encode())

    # Store the encrypted value in the SQLite database
    cursor.execute('''
        INSERT INTO secrets (name, encrypted_value) 
        VALUES (?, ?)
    ''', (secret_name, encrypted_value))

    # Commit changes and close the connection
    conn.commit()
    conn.close()

    # Generate the Vault reference
    reference = f"op://vault/sentinelai/{secret_name.lower().replace(' ', '-')}"
    print(f"Secret '{secret_name}' stored. Reference: {reference}")

    return reference

# Function to retrieve a secret (decrypt it)
def get_secret(secret_name: str) -> str:
    # Load the Fernet key from the vault.key file
    with open(KEY_FILE, 'rb') as key_file:
        key = key_file.read()

    # Create a Fernet cipher object using the loaded key
    cipher = Fernet(key)

    # Retrieve the encrypted value from the SQLite database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT encrypted_value FROM secrets WHERE name = ?
    ''', (secret_name,))
    result = cursor.fetchone()

    # If the secret exists, decrypt it
    if result:
        encrypted_value = result[0]
        decrypted_value = cipher.decrypt(encrypted_value).decode()
        conn.close()
        print(f"Secret '{secret_name}' retrieved and decrypted.")
        return decrypted_value
    else:
        conn.close()
        print(f"Secret '{secret_name}' not found in the database.")
        return None

# Function to get all secrets from the vault
def get_all_secrets() -> list[dict]:
    # Load the Fernet key from the vault.key file
    with open(KEY_FILE, 'rb') as f:
        cipher = Fernet(f.read())
    
    # Connect to the SQLite database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get all secrets from the database
    cursor.execute('SELECT name, encrypted_value FROM secrets')
    rows = cursor.fetchall()

    # Close the connection
    conn.close()

    results = []
    for name, encrypted_value in rows:
        # Decrypt the secret
        decrypted = cipher.decrypt(encrypted_value).decode()
        
        # Generate the Vault reference
        reference = f"op://vault/sentinelai/{name.lower().replace(' ', '-')}"
        
        # Add to the results
        results.append({"name": name, "value": decrypted, "reference": reference})

    return results

# Initialize database
DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'audit.db')

def init_db():
    """Initializes the database table."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            repo_name TEXT,
            secrets_found INTEGER,
            secret_types TEXT,
            action TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_push(repo_path: str, findings: list, action: str):
    """
    Inserts a new entry into the audit_log table.
    - findings: Expected to be a list of dicts with a 'type' key.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Process data
    timestamp = datetime.now().isoformat()
    repo_name = repo_path.split('/')[-1] # Simple parsing
    secrets_count = len(findings)
    # Store types as comma-separated string or JSON string
    secret_types = ",".join(set(f.get('label', 'unknown') for f in findings))
    
    cursor.execute('''
        INSERT INTO audit_log (timestamp, repo_name, secrets_found, secret_types, action)
        VALUES (?, ?, ?, ?, ?)
    ''', (timestamp, repo_name, secrets_count, secret_types, action))
    
    conn.commit()
    conn.close()

def get_audit_log() -> list[dict]:
    """Returns all rows from audit_log."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row # Access columns by name
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM audit_log ORDER BY timestamp DESC')
    
    rows = cursor.fetchall()
    conn.close()
    
    # Convert rows to dictionaries
    return [dict(row) for row in rows]

# Example usage
if __name__ == "__main__":
    # Initialize the Vault (generate key and set up database)
    init_vault()

    # Store a new secret in the vault
    store_secret("my_aws_access_key", "op://vault/sentinelai/aws-access-keyE")

    # Retrieve and decrypt the secret
    secret_value = get_secret("my_aws_access_key")
    if secret_value:
        print(f"Retrieved secret: {secret_value}")

    # Get all secrets from the database
    all_secrets = get_all_secrets()
    for secret in all_secrets:
        print(f"Name: {secret['name']}, Value: {secret['value']}, Reference: {secret['reference']}")