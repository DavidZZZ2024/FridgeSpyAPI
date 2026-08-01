import logging

import snowflake.connector
from fastapi import APIRouter, HTTPException, Query

from app.schemas.products import ProductListResponse, StatisticsResponse
from app.services.snowflake_service import fetch_all, fetch_one

router = APIRouter(tags=["Statistics"])
logger = logging.getLogger("fridgespy.statistics")
SOURCE = "FRIDGE_DB.RAW.VW_FRIDGES_RAW"


@router.get("/statistics", response_model=StatisticsResponse)
def get_statistics():
    sql = f"""
        SELECT COUNT(*) AS total_products,
               COUNT(DISTINCT brand) AS total_brands,
               COUNT(DISTINCT retailer) AS total_retailers,
               MIN(price_raw) AS minimum_price,
               AVG(price_raw) AS average_price,
               MAX(price_raw) AS maximum_price
        FROM {SOURCE}
    """
    try:
        return fetch_one(sql) or {
            "total_products": 0, "total_brands": 0, "total_retailers": 0,
            "minimum_price": None, "average_price": None, "maximum_price": None,
        }
    except (snowflake.connector.errors.Error, RuntimeError) as exc:
        logger.exception("Failed to retrieve statistics")
        raise HTTPException(status_code=500, detail="Unable to retrieve statistics") from exc


@router.get("/lowest-price", response_model=ProductListResponse)
def get_lowest_price(limit: int = Query(default=10, ge=1, le=100)):
    sql = f"""
        SELECT retailer, brand, title, model, price_raw, date_raw
        FROM {SOURCE}
        WHERE price_raw IS NOT NULL
        ORDER BY price_raw ASC
        LIMIT %s
    """
    try:
        products = fetch_all(sql, (limit,))
        return {"count": len(products), "products": products}
    except (snowflake.connector.errors.Error, RuntimeError) as exc:
        logger.exception("Failed to retrieve lowest-price products")
        raise HTTPException(status_code=500, detail="Unable to retrieve product data") from exc
