import logging

import snowflake.connector
from fastapi import APIRouter, HTTPException

from app.schemas.products import BrandListResponse, RetailerListResponse
from app.services.snowflake_service import fetch_all

router = APIRouter(tags=["Metadata"])
logger = logging.getLogger("fridgespy.metadata")
SOURCE = "FRIDGE_DB.RAW.VW_FRIDGES_RAW"


@router.get("/brands", response_model=BrandListResponse)
def get_brands():
    try:
        rows = fetch_all(f"SELECT DISTINCT brand FROM {SOURCE} WHERE brand IS NOT NULL ORDER BY brand ASC")
        brands = [row["brand"] for row in rows]
        return {"count": len(brands), "brands": brands}
    except (snowflake.connector.errors.Error, RuntimeError) as exc:
        logger.exception("Failed to retrieve brands")
        raise HTTPException(status_code=500, detail="Unable to retrieve metadata") from exc


@router.get("/retailers", response_model=RetailerListResponse)
def get_retailers():
    try:
        rows = fetch_all(f"SELECT DISTINCT retailer FROM {SOURCE} WHERE retailer IS NOT NULL ORDER BY retailer ASC")
        retailers = [row["retailer"] for row in rows]
        return {"count": len(retailers), "retailers": retailers}
    except (snowflake.connector.errors.Error, RuntimeError) as exc:
        logger.exception("Failed to retrieve retailers")
        raise HTTPException(status_code=500, detail="Unable to retrieve metadata") from exc
