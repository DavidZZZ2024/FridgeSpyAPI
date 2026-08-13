from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_products: int
    total_brands: int
    total_retailers: int
    average_price: float | None
    median_price: float | None
    latest_date: str | None


class GroupStatistics(BaseModel):
    product_count: int
    average_price: float | None


class RetailerStatistics(GroupStatistics):
    retailer: str


class BrandStatistics(GroupStatistics):
    brand: str


class PriceDistributionBucket(BaseModel):
    range: str
    count: int
    sort_order: int


class PriceTrendPoint(BaseModel):
    date: str
    average_price: float
    product_count: int
