from pydantic import BaseModel


class Product(BaseModel):
    retailer: str | None = None
    brand: str | None = None
    title: str | None = None
    model: str | None = None
    price_raw: float | None = None
    url: str | None = None
    date_raw: str | None = None


class ProductListResponse(BaseModel):
    count: int
    products: list[Product]


class BrandListResponse(BaseModel):
    count: int
    brands: list[str]


class RetailerListResponse(BaseModel):
    count: int
    retailers: list[str]


class StatisticsResponse(BaseModel):
    total_products: int
    total_brands: int
    total_retailers: int
    minimum_price: float | None
    average_price: float | None
    maximum_price: float | None


class PriceHistoryItem(BaseModel):
    date_raw: str
    retailer: str | None = None
    price_raw: float


class PriceHistoryResponse(BaseModel):
    model: str
    count: int
    history: list[PriceHistoryItem]
