from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
from typing import Optional

class NewProduct(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    price: int = Field(..., gt=0)
    category: str = Field(..., min_length=2)
    in_stock: bool = True

app = FastAPI()

products = [
    {"id": 1, "name": "Wireless Mouse", "price": 599, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
    {"id": 4, "name": "USB Cable", "price": 199, "category": "Electronics", "in_stock": False},
    {"id": 5, "name": "Laptop Stand", "price": 1299, "category": "Electronics", "in_stock": True},
    {"id": 6, "name": "Mechanical Keyboard", "price": 2499, "category": "Electronics", "in_stock": True},
    {"id": 7, "name": "Webcam", "price": 1899, "category": "Electronics", "in_stock": False}
]
feedback = []
orders = []

@app.get("/")
def home():
    return {"message": "Welcome to our app"}
@app.get("/products")
def get_products():
    return {
        "products": products,
        "total": len(products)
    }
@app.get("/products/category/{category_name}")
def get_by_category(category_name: str):

    result = [p for p in products if p["category"] == category_name]

    if not result:
        return {"error": "No products found in this category"}

    return {
        "category": category_name,
        "products": result,
        "total": len(result)
    }
@app.get("/products/instock")
def get_instock():

    available = [p for p in products if p["in_stock"] == True]

    return {
        "in_stock_products": available,
        "count": len(available)
    }
@app.get("/store/summary")
def store_summary():

    in_stock_count = len([p for p in products if p["in_stock"]])
    out_stock_count = len(products) - in_stock_count
    categories = list(set([p["category"] for p in products]))

    return {
        "store_name": "My E-commerce Store",
        "total_products": len(products),
        "in_stock": in_stock_count,
        "out_of_stock": out_stock_count,
        "categories": categories
    }
@app.get("/products/search/{keyword}")
def search_products(keyword: str):

    results = [
        p for p in products
        if keyword.lower() in p["name"].lower()
    ]

    if not results:
        return {"message": "No products matched your search"}

    return {
        "keyword": keyword,
        "results": results,
        "total_matches": len(results)
    }
from typing import Optional
from fastapi import Query

@app.get("/products/filter")
def filter_products(
    category: Optional[str] = None,
    max_price: Optional[int] = None,
    min_price: Optional[int] = Query(None, description="Minimum price")
):

    result = products

    if category:
        result = [p for p in result if p["category"].lower() == category.lower()]

    if max_price is not None:
        result = [p for p in result if p["price"] <= max_price]

    if min_price is not None:
        result = [p for p in result if p["price"] >= min_price]

    return {
        "filtered_products": result,
        "count": len(result)
    }
@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):

    for product in products:
        if product["id"] == product_id:
            return {
                "name": product["name"],
                "price": product["price"]
            }

    return {"error": "Product not found"}
class CustomerFeedback(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=100)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)
class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
class BulkOrder(BaseModel):
    customer_name: str = Field(..., min_length=2)
    items: list[OrderItem]
@app.post("/feedback")
def submit_feedback(data: CustomerFeedback):

    feedback.append(data.dict())

    return {
        "message": "Feedback submitted successfully",
        "feedback": data.dict(),
        "total_feedback": len(feedback)
    }
@app.get("/products/summary")
def product_summary():

    in_stock = [p for p in products if p["in_stock"]]
    out_of_stock = [p for p in products if not p["in_stock"]]

    most_expensive = max(products, key=lambda p: p["price"])
    cheapest = min(products, key=lambda p: p["price"])

    categories = list(set(p["category"] for p in products))

    return {
        "total_products": len(products),
        "in_stock_count": len(in_stock),
        "out_of_stock_count": len(out_of_stock),
        "most_expensive": {
            "name": most_expensive["name"],
            "price": most_expensive["price"]
        },
        "cheapest": {
            "name": cheapest["name"],
            "price": cheapest["price"]
        },
        "categories": categories
    }
@app.post("/orders/bulk")
def create_bulk_order(order: BulkOrder):

    confirmed = []
    failed = []
    grand_total = 0

    for item in order.items:

        product = next((p for p in products if p["id"] == item.product_id), None)

        if not product:
            failed.append({
                "product_id": item.product_id,
                "reason": "Product not found"
            })
            continue

        if not product["in_stock"]:
            failed.append({
                "product_id": item.product_id,
                "product_name": product["name"],
                "reason": "Out of stock"
            })
            continue

        item_total = product["price"] * item.quantity
        grand_total += item_total

        confirmed.append({
            "product_name": product["name"],
            "quantity": item.quantity,
            "item_total": item_total
        })

    order_data = {
        "id": len(orders) + 1,
        "customer": order.customer_name,
        "confirmed": confirmed,
        "failed": failed,
        "grand_total": grand_total,
        "status": "pending"
    }

    orders.append(order_data)

    return order_data
@app.patch("/orders/{order_id}/confirm")
def confirm_order(order_id: int):

    for order in orders:
        if order["id"] == order_id:
            order["status"] = "confirmed"
            return {
                "message": "Order confirmed",
                "order": order
            }

    return {"error": "Order not found"}
@app.post("/products")
def add_product(new_product: NewProduct):

    existing_names = [p["name"].lower() for p in products]

    if new_product.name.lower() in existing_names:
        return {"error": "Product with this name already exists"}

    new_id = max(p["id"] for p in products) + 1

    product = {
        "id": new_id,
        "name": new_product.name,
        "price": new_product.price,
        "category": new_product.category,
        "in_stock": new_product.in_stock
    }

    products.append(product)

    return {
        "message": "Product added",
        "product": product
    }
@app.put("/products/{product_id}")
def update_product(product_id: int, price: int = None, in_stock: bool = None):

    for p in products:
        if p["id"] == product_id:

            if price is not None:
                p["price"] = price

            if in_stock is not None:
                p["in_stock"] = in_stock

            return {"message": "Product updated", "product": p}

    return {"error": "Product not found"}
@app.delete("/products/{product_id}")
def delete_product(product_id: int):

    for p in products:
        if p["id"] == product_id:
            products.remove(p)
            return {"message": f"{p['name']} deleted"}

    return {"error": "Product not found"}
@app.get("/products/audit")
def product_audit():

    in_stock_products = [p for p in products if p["in_stock"]]

    out_stock_products = [p["name"] for p in products if not p["in_stock"]]

    total_stock_value = sum(p["price"] * 10 for p in in_stock_products)

    most_expensive = max(products, key=lambda p: p["price"])

    return {
        "total_products": len(products),
        "in_stock_count": len(in_stock_products),
        "out_of_stock_names": out_stock_products,
        "total_stock_value": total_stock_value,
        "most_expensive": {
            "name": most_expensive["name"],
            "price": most_expensive["price"]
        }
    }
@app.put("/products/discount")
def apply_discount(category: str, discount_percent: int):

    updated = []

    for p in products:
        if p["category"].lower() == category.lower():

            discount = p["price"] * discount_percent / 100
            p["price"] = int(p["price"] - discount)

            updated.append(p)

    return {"updated_products": updated}