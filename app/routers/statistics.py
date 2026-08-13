import logging

import snowflake.connector
from fastapi import APIRouter, HTTPException, Query

from app.schemas.products import ProductListResponse, StatisticsResponse
from app.schemas.statistics import (
    BrandStatistics,
    DashboardSummary,
    PriceDistributionBucket,
    PriceTrendPoint,
    RetailerStatistics,
)
from app.services.snowflake_service import fetch_all, fetch_one

router = APIRouter(tags=["Statistics"])
logger = logging.getLogger("fridgespy.statistics")
SOURCE = "FRIDGE_DB.RAW.VW_FRIDGES_RAW"

# Dashboard snapshot metrics use the latest parseable scrape date and one row per
# retailer/product identity. Model is preferred as the stable identity, with title
# as a fallback for rows where no model was extracted.
SNAPSHOT_CTE = f"""
    latest_date AS (
        SELECT MAX(TRY_TO_DATE(date_raw::VARCHAR)) AS scrape_date
        FROM {SOURCE}
        WHERE TRY_TO_DATE(date_raw::VARCHAR) IS NOT NULL
    ),
    snapshot AS (
        SELECT retailer, brand, title, model, price_raw,
               TRY_TO_DATE(date_raw::VARCHAR) AS scrape_date
        FROM {SOURCE}
        CROSS JOIN latest_date
        WHERE TRY_TO_DATE(date_raw::VARCHAR) = latest_date.scrape_date
          AND COALESCE(NULLIF(TRIM(model), ''), NULLIF(TRIM(title), '')) IS NOT NULL
        QUALIFY ROW_NUMBER() OVER (
            PARTITION BY
                COALESCE(NULLIF(TRIM(retailer), ''), 'Unknown retailer'),
                COALESCE(NULLIF(TRIM(model), ''), NULLIF(TRIM(title), ''))
            ORDER BY IFF(price_raw IS NULL OR price_raw < 0, 1, 0), price_raw, title
        ) = 1
    )
"""


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


@router.get("/statistics/summary", response_model=DashboardSummary)
def get_statistics_summary():
    sql = f"""
        WITH {SNAPSHOT_CTE}
        SELECT COUNT(*) AS total_products,
               COUNT(DISTINCT NULLIF(TRIM(brand), '')) AS total_brands,
               COUNT(DISTINCT NULLIF(TRIM(retailer), '')) AS total_retailers,
               AVG(IFF(price_raw >= 0, price_raw, NULL)) AS average_price,
               MEDIAN(IFF(price_raw >= 0, price_raw, NULL)) AS median_price,
               MAX(scrape_date) AS latest_date
        FROM snapshot
    """
    try:
        return fetch_one(sql) or {
            "total_products": 0,
            "total_brands": 0,
            "total_retailers": 0,
            "average_price": None,
            "median_price": None,
            "latest_date": None,
        }
    except (snowflake.connector.errors.Error, RuntimeError) as exc:
        logger.exception("Failed to retrieve dashboard summary")
        raise HTTPException(status_code=500, detail="Unable to retrieve dashboard summary") from exc


@router.get("/statistics/retailers", response_model=list[RetailerStatistics])
def get_retailer_statistics():
    sql = f"""
        WITH {SNAPSHOT_CTE}
        SELECT TRIM(retailer) AS retailer,
               COUNT(*) AS product_count,
               AVG(IFF(price_raw >= 0, price_raw, NULL)) AS average_price
        FROM snapshot
        WHERE NULLIF(TRIM(retailer), '') IS NOT NULL
        GROUP BY TRIM(retailer)
        ORDER BY product_count DESC, retailer ASC
    """
    try:
        return fetch_all(sql)
    except (snowflake.connector.errors.Error, RuntimeError) as exc:
        logger.exception("Failed to retrieve retailer statistics")
        raise HTTPException(status_code=500, detail="Unable to retrieve retailer statistics") from exc


@router.get("/statistics/brands", response_model=list[BrandStatistics])
def get_brand_statistics():
    sql = f"""
        WITH {SNAPSHOT_CTE}
        SELECT TRIM(brand) AS brand,
               COUNT(*) AS product_count,
               AVG(IFF(price_raw >= 0, price_raw, NULL)) AS average_price
        FROM snapshot
        WHERE NULLIF(TRIM(brand), '') IS NOT NULL
        GROUP BY TRIM(brand)
        ORDER BY product_count DESC, brand ASC
    """
    try:
        return fetch_all(sql)
    except (snowflake.connector.errors.Error, RuntimeError) as exc:
        logger.exception("Failed to retrieve brand statistics")
        raise HTTPException(status_code=500, detail="Unable to retrieve brand statistics") from exc


@router.get("/statistics/price-distribution", response_model=list[PriceDistributionBucket])
def get_price_distribution():
    sql = f"""
        WITH {SNAPSHOT_CTE},
        buckets AS (
            SELECT column1 AS price_range, column2 AS sort_order
            FROM VALUES
                ('Under $500', 1),
                ('$500–$999', 2),
                ('$1,000–$1,499', 3),
                ('$1,500–$1,999', 4),
                ('$2,000–$2,999', 5),
                ('$3,000+', 6)
        ),
        bucket_counts AS (
            SELECT CASE
                       WHEN price_raw < 500 THEN 'Under $500'
                       WHEN price_raw < 1000 THEN '$500–$999'
                       WHEN price_raw < 1500 THEN '$1,000–$1,499'
                       WHEN price_raw < 2000 THEN '$1,500–$1,999'
                       WHEN price_raw < 3000 THEN '$2,000–$2,999'
                       ELSE '$3,000+'
                   END AS price_range,
                   COUNT(*) AS count
            FROM snapshot
            WHERE price_raw IS NOT NULL AND price_raw >= 0
            GROUP BY price_range
        )
        SELECT buckets.price_range AS "range",
               COALESCE(bucket_counts.count, 0) AS count,
               buckets.sort_order
        FROM buckets
        LEFT JOIN bucket_counts ON bucket_counts.price_range = buckets.price_range
        ORDER BY buckets.sort_order
    """
    try:
        return fetch_all(sql)
    except (snowflake.connector.errors.Error, RuntimeError) as exc:
        logger.exception("Failed to retrieve price distribution")
        raise HTTPException(status_code=500, detail="Unable to retrieve price distribution") from exc


@router.get("/statistics/price-trend", response_model=list[PriceTrendPoint])
def get_price_trend():
    sql = f"""
        WITH dated_products AS (
            SELECT TRY_TO_DATE(date_raw::VARCHAR) AS scrape_date,
                   retailer, model, title, price_raw
            FROM {SOURCE}
            WHERE TRY_TO_DATE(date_raw::VARCHAR) IS NOT NULL
              AND price_raw IS NOT NULL
              AND price_raw >= 0
              AND COALESCE(NULLIF(TRIM(model), ''), NULLIF(TRIM(title), '')) IS NOT NULL
            QUALIFY ROW_NUMBER() OVER (
                PARTITION BY
                    TRY_TO_DATE(date_raw::VARCHAR),
                    COALESCE(NULLIF(TRIM(retailer), ''), 'Unknown retailer'),
                    COALESCE(NULLIF(TRIM(model), ''), NULLIF(TRIM(title), ''))
                ORDER BY price_raw, title
            ) = 1
        )
        SELECT scrape_date AS date,
               AVG(price_raw) AS average_price,
               COUNT(*) AS product_count
        FROM dated_products
        GROUP BY scrape_date
        ORDER BY scrape_date ASC
    """
    try:
        return fetch_all(sql)
    except (snowflake.connector.errors.Error, RuntimeError) as exc:
        logger.exception("Failed to retrieve price trend")
        raise HTTPException(status_code=500, detail="Unable to retrieve price trend") from exc


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
