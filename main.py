from fastapi import FastAPI

app = FastAPI(
    title="FridgeSpy API",
    description="API for Australian fridge price comparison",
    version="1.0.0",
)

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
def get_products():
    return {
        "products": [
            {
                "retailer": "JB Hi-Fi",
                "brand": "Samsung",
                "model": "SRF7500BB",
                "price": 1999.00,
            },
            {
                "retailer": "The Good Guys",
                "brand": "LG",
                "model": "GB455UPLE",
                "price": 1299.00,
            },
        ]
    }
