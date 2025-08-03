# main.py
from fastapi import FastAPI
import requests

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "NutriScan API is live!"}

@app.get("/product/{barcode}")
def get_product_info(barcode: str):
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    res = requests.get(url)
    data = res.json()

    if data.get("status") == 1:
        product = data["product"]
        return {
            "name": product.get("product_name", "N/A"),
            "brand": product.get("brands", "N/A"),
            "quantity": product.get("quantity", "N/A"),
            "ingredients": product.get("ingredients_text", "N/A"),
            "nutriments": product.get("nutriments", {})
        }
    else:
        return {"error": "Product not found"}

