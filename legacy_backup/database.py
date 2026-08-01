# import os

# import snowflake.connector
# from dotenv import load_dotenv

# load_dotenv()


# def get_snowflake_connection():
#     required_vars = [
#         "SNOWFLAKE_ACCOUNT",
#         "SNOWFLAKE_USER",
#         "SNOWFLAKE_PASSWORD",
#         "SNOWFLAKE_WAREHOUSE",
#         "SNOWFLAKE_DATABASE",
#         "SNOWFLAKE_SCHEMA",
#         "SNOWFLAKE_ROLE",
#     ]

#     missing_vars = [var for var in required_vars if not os.getenv(var)]
#     if missing_vars:
#         missing_list = ", ".join(missing_vars)
#         raise RuntimeError(f"Missing required Snowflake environment variables: {missing_list}")

#     return snowflake.connector.connect(
#         account=os.getenv("SNOWFLAKE_ACCOUNT"),
#         user=os.getenv("SNOWFLAKE_USER"),
#         password=os.getenv("SNOWFLAKE_PASSWORD"),
#         passcode=os.getenv("SNOWFLAKE_PASSCODE"),
#         warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
#         database=os.getenv("SNOWFLAKE_DATABASE"),
#         schema=os.getenv("SNOWFLAKE_SCHEMA"),
#         role=os.getenv("SNOWFLAKE_ROLE"),
#         login_timeout=20,
#         network_timeout=30,
#         application="FridgeSpyAPI",
#     )

import os
from pathlib import Path

import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent


def get_required_env(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")

    return value


def get_snowflake_connection():
    private_key_path = Path(
        get_required_env("SNOWFLAKE_PRIVATE_KEY_FILE")
    )

    if not private_key_path.is_absolute():
        private_key_path = BASE_DIR / private_key_path

    if not private_key_path.exists():
        raise RuntimeError(
            f"Snowflake private key file was not found: {private_key_path}"
        )

    return snowflake.connector.connect(
        account=get_required_env("SNOWFLAKE_ACCOUNT"),
        user=get_required_env("SNOWFLAKE_USER"),
        warehouse=get_required_env("SNOWFLAKE_WAREHOUSE"),
        database=get_required_env("SNOWFLAKE_DATABASE"),
        schema=get_required_env("SNOWFLAKE_SCHEMA"),
        role=get_required_env("SNOWFLAKE_ROLE"),
        authenticator="SNOWFLAKE_JWT",
        private_key_file=str(private_key_path),
        private_key_file_pwd=get_required_env(
            "SNOWFLAKE_PRIVATE_KEY_PASSWORD"
        ),
        login_timeout=20,
        network_timeout=30,
        application="FridgeSpyAPI",
    )