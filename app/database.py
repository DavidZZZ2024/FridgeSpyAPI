import os
from pathlib import Path

import snowflake.connector
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from dotenv import load_dotenv

load_dotenv()

# Keep relative key paths anchored where the original database.py lived.
BASE_DIR = Path(__file__).resolve().parent.parent


def get_required_env(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")

    return value


def get_snowflake_connection():
    private_key_pem = os.getenv("SNOWFLAKE_PRIVATE_KEY")
    private_key_file = os.getenv("SNOWFLAKE_PRIVATE_KEY_FILE")

    connection_kwargs = {
        "account": get_required_env("SNOWFLAKE_ACCOUNT"),
        "user": get_required_env("SNOWFLAKE_USER"),
        "warehouse": get_required_env("SNOWFLAKE_WAREHOUSE"),
        "database": get_required_env("SNOWFLAKE_DATABASE"),
        "schema": get_required_env("SNOWFLAKE_SCHEMA"),
        "role": get_required_env("SNOWFLAKE_ROLE"),
        "authenticator": "SNOWFLAKE_JWT",
        "login_timeout": 20,
        "network_timeout": 30,
        "application": "FridgeSpyAPI",
    }

    if private_key_pem:
        normalized_pem = private_key_pem.replace("\\n", "\n").encode("utf-8")
        password = get_required_env("SNOWFLAKE_PRIVATE_KEY_PASSWORD").encode("utf-8")
        loaded_key = load_pem_private_key(normalized_pem, password=password)
        private_key_der = loaded_key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        connection_kwargs["private_key"] = private_key_der
    elif private_key_file:
        private_key_path = Path(private_key_file)

        if not private_key_path.is_absolute():
            private_key_path = BASE_DIR / private_key_path

        if not private_key_path.exists():
            raise RuntimeError("Snowflake private key file was not found")

        connection_kwargs["private_key_file"] = str(private_key_path)
        connection_kwargs["private_key_file_pwd"] = get_required_env(
            "SNOWFLAKE_PRIVATE_KEY_PASSWORD"
        )
    else:
        raise RuntimeError(
            "Set SNOWFLAKE_PRIVATE_KEY or SNOWFLAKE_PRIVATE_KEY_FILE"
        )

    return snowflake.connector.connect(**connection_kwargs)
