import logging

import snowflake.connector
from fastapi import FastAPI, HTTPException, Query
from snowflake.connector import DictCursor

from database import get_snowflake_connection

app = FastAPI(
    title="FridgeSpy API",
    description="API for Australian fridge price comparison",
    version="1.0.0",
)

logger = logging.getLogger("fridgespy")


@app.get("/")
def home():
    return {
        "message": "FridgeSpy API is running",
        "status": "healthy",
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }


@app.get("/products")
def get_products(limit: int = Query(default=100, ge=1, le=500)):
    query = """
        SELECT
            retailer,
            brand,
            title,
            model,
            price_raw
        FROM FRIDGE_DB.RAW.VW_FRIDGES_RAW
        WHERE price_raw IS NOT NULL
        ORDER BY price_raw ASC
        LIMIT %s
    """

    connection = None
    cursor = None

    try:
        connection = get_snowflake_connection()
        cursor = connection.cursor(DictCursor)
        cursor.execute(query, (limit,))
        rows = cursor.fetchall()

        products = []
        for row in rows:
            product = {
                "retailer": row.get("RETAILER"),
                "brand": row.get("BRAND"),
                "title": row.get("TITLE"),
                "model": row.get("MODEL"),
                "price_raw": float(row["PRICE_RAW"]) if row.get("PRICE_RAW") is not None else None,
                "url": row.get("URL"),
            }
            products.append(product)

        return {
            "count": len(products),
            "products": products,
        }
    except (snowflake.connector.errors.Error, RuntimeError) as exc:
        logger.exception("Failed to retrieve products from Snowflake")
        raise HTTPException(status_code=500, detail="Unable to retrieve products from Snowflake") from exc
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


@app.get("/database-health")
def database_health():
    connection = None
    cursor = None

    try:
        connection = get_snowflake_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT CURRENT_VERSION()")
        row = cursor.fetchone()
        version = row[0] if row else None

        return {
            "status": "ok",
            "snowflake_version": version,
        }
    except (snowflake.connector.errors.Error, RuntimeError) as exc:
        logger.exception("Snowflake connection check failed")
        raise HTTPException(status_code=503, detail="Snowflake connection unavailable") from exc
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()
