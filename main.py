# main.py
from fastapi import FastAPI
import requests
import os
import google.generativeai as genai

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=GOOGLE_API_KEY)

def get_gemini_summary(text):
    model = genai.GenerativeModel('gemini-2.5-flash')
    price_prompt = f"Given a food product with the following details:\n{text}\n\nProvide its exact price in Indian Rupees. Just return the value in numbers, no text. You can check online for the latest price. If price is not available, just return 'N/A'."
    price_response = model.generate_content(price_prompt)
    price = price_response.text.strip()

    nutriscore_prompt = f"Given a food product with the following details:\n{text}\n\nProvide a NutriScore out of 10 based on its nutritional content. Just return the number, no text."
    nutriscore_response = model.generate_content(nutriscore_prompt)
    nutriscore = nutriscore_response.text.strip()

    rcmd_intake_prompt = f"Given a food product with the following details:\n{text}\n\nProvide a recommended daily intake in a suitable unit. Just return the value in numbers, no text."
    rcmd_intake_response = model.generate_content(rcmd_intake_prompt)
    rcmd_intake = rcmd_intake_response.text.strip()

    return {
        "price": price,
        "nutriscore": nutriscore,
        "recommended_intake": rcmd_intake
    }


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
        nutriments = product.get("nutriments", {})
        # Build a string summary of the product's info
        info = (
            f"Name: {product.get('product_name', 'N/A')}\n"
            f"Brand: {product.get('brands', 'N/A')}\n"
            f"Quantity: {product.get('quantity', 'N/A')}\n"
            f"Ingredients: {product.get('ingredients_text', 'N/A')}\n"
            f"Nutriments: {nutriments}\n"
        )
        # Get AI summary
        summary = get_gemini_summary(info)
        return {
            "name": product.get("product_name", "N/A"),
            "brand": product.get("brands", "N/A"),
            "quantity": product.get("quantity", "N/A"),
            "ingredients": product.get("ingredients_text", "N/A"),
            "nutriments": nutriments,
            "price": summary.get("price"),
            "nutriscore": summary.get("nutriscore"),
            "recommended_intake": summary.get("recommended_intake")
        }
    else:
        return {"error": "Product not found"}
