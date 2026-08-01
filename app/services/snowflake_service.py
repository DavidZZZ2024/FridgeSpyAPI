from datetime import date, datetime
from decimal import Decimal
from typing import Any

from snowflake.connector import DictCursor

from app.database import get_snowflake_connection


def _serialize_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def _normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    return {key.lower(): _serialize_value(value) for key, value in row.items()}


def fetch_all(sql: str, params: tuple | None = None) -> list[dict]:
    connection = None
    cursor = None
    try:
        connection = get_snowflake_connection()
        cursor = connection.cursor(DictCursor)
        cursor.execute(sql, params or ())
        return [_normalize_row(row) for row in cursor.fetchall()]
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


def fetch_one(sql: str, params: tuple | None = None) -> dict | None:
    connection = None
    cursor = None
    try:
        connection = get_snowflake_connection()
        cursor = connection.cursor(DictCursor)
        cursor.execute(sql, params or ())
        row = cursor.fetchone()
        return _normalize_row(row) if row is not None else None
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()
