import json
import os
import logging
from fastapi import FastAPI, HTTPException
from .parse_mcdonald import parse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()


@app.on_event("startup")
async def start_event():
    logger.info("Go to http://127.0.0.1:8000/docs to see api endpoints")


@app.get("/load_menu/")
async def load_menu():
    try:
        parse()
        message = 'ok'

    except Exception as e:
        message = e

    return {'Response': message}


@app.get("/all_products/")
async def read_all_products():
    if os.path.exists("app/menu.json") and os.path.getsize("app/menu.json") > 0:
        return get_menu()

    raise HTTPException(status_code=404, detail="Menu not found")


@app.get("/products/{product_name}")
async def read_product(product_name: str):
    menu_data = get_menu()

    for product in menu_data:
        if product.get("Name", "").lower() == product_name.lower():
            return product
    raise HTTPException(status_code=404, detail="Product not found")


@app.get("/products/{product_name}/{product_field}")
async def read_product_field(product_name: str, product_field: str):
    menu_data = get_menu()
    for product in menu_data:
        if product.get("Name").lower() == product_name.lower():
            print(f" {product_name}: {product_field}")
            if product_field in product:
                return {product_field: product[product_field]}
            else:
                raise HTTPException(status_code=404, detail="Field not found in the product")
    raise HTTPException(status_code=404, detail="Product not found")


def get_menu():
    with open('app/menu.json', 'r', encoding='utf-8') as file:
        return json.load(file)