import logging

import snowflake.connector
from fastapi import APIRouter, HTTPException, Query

from app.schemas.products import PriceHistoryResponse, ProductListResponse
from app.services.snowflake_service import fetch_all

router = APIRouter(prefix="/products", tags=["Products"])
logger = logging.getLogger("fridgespy.products")
SOURCE = "FRIDGE_DB.RAW.VW_FRIDGES_RAW"


def _snowflake_failure(message: str, exc: Exception) -> HTTPException:
    logger.exception(message)
    return HTTPException(status_code=500, detail="Unable to retrieve product data")


@router.get("", response_model=ProductListResponse)
def get_products(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    brand: str | None = None,
    retailer: str | None = None,
    min_price: float | None = Query(default=None, ge=0),
    max_price: float | None = Query(default=None, ge=0),
    search: str | None = None,
):
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(status_code=400, detail="min_price cannot exceed max_price")

    filters = ["price_raw IS NOT NULL"]
    params: list[object] = []
    if brand is not None:
        filters.append("LOWER(brand) = LOWER(%s)")
        params.append(brand)
    if retailer is not None:
        filters.append("LOWER(retailer) = LOWER(%s)")
        params.append(retailer)
    if min_price is not None:
        filters.append("price_raw >= %s")
        params.append(min_price)
    if max_price is not None:
        filters.append("price_raw <= %s")
        params.append(max_price)
    if search is not None:
        filters.append("(title ILIKE %s OR model ILIKE %s)")
        pattern = f"%{search}%"
        params.extend((pattern, pattern))

    sql = f"""
        SELECT retailer, brand, title, model, price_raw, date_raw
        FROM {SOURCE}
        WHERE {' AND '.join(filters)}
        AND date_raw = DATEADD(
            day,
            -1,
            CONVERT_TIMEZONE(
                'Australia/Melbourne',
                CURRENT_TIMESTAMP()
            )::DATE
        )
        ORDER BY price_raw DESC
        LIMIT %s OFFSET %s
    """
    params.extend((limit, offset))
    try:
        products = fetch_all(sql, tuple(params))
        return {"count": len(products), "products": products}
    except (snowflake.connector.errors.Error, RuntimeError) as exc:
        raise _snowflake_failure("Failed to retrieve products", exc) from exc


@router.get("/{model}/price-history", response_model=PriceHistoryResponse)
def get_price_history(model: str):
    sql = f"""
        SELECT date_raw, retailer, price_raw
        FROM {SOURCE}
        WHERE LOWER(model) = LOWER(%s)
          AND date_raw IS NOT NULL
          AND price_raw IS NOT NULL
        ORDER BY date_raw ASC
    """
    try:
        history = fetch_all(sql, (model,))
    except (snowflake.connector.errors.Error, RuntimeError) as exc:
        raise _snowflake_failure("Failed to retrieve price history", exc) from exc
    if not history:
        raise HTTPException(status_code=404, detail="Price history not found")
    return {"model": model, "count": len(history), "history": history}


@router.get("/{model}", response_model=ProductListResponse)
def get_product_offers(model: str):
    sql = f"""
        SELECT retailer, brand, title, model, price_raw, date_raw
        FROM {SOURCE}
        WHERE LOWER(model) = LOWER(%s)
        ORDER BY price_raw ASC
    """
    try:
        products = fetch_all(sql, (model,))
    except (snowflake.connector.errors.Error, RuntimeError) as exc:
        raise _snowflake_failure("Failed to retrieve product offers", exc) from exc
    if not products:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"count": len(products), "products": products}
