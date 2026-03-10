from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional, List
from typing import List


app = FastAPI()
feedback = []


products = [
    {"id": 1, "name": "Wireless Mouse", "price": 599, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 120, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": False},
    {"id": 4, "name": "Desk Lamp", "price": 899, "category": "Electronics", "in_stock": True},

    {"id": 5, "name": "Laptop Stand", "price": 1500, "category": "Electronics", "in_stock": True},
    {"id": 6, "name": "Mechanical Keyboard", "price": 2499, "category": "Electronics", "in_stock": True},
    {"id": 7, "name": "Webcam", "price": 1200, "category": "Electronics", "in_stock": False}
]
orders = []
order_counter = 1
from pydantic import BaseModel, Field

class Order(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1)
class CustomerFeedback(BaseModel):
    customer_name: str = Field(..., min_length=2)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)

class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1, le=50)


class BulkOrder(BaseModel):
    company_name: str = Field(..., min_length=2)
    contact_email: str
    items: List[OrderItem]

@app.get("/products")
def get_products():
    return {
        "products": products,
        "total": len(products)
    }

# Q2
@app.get("/products/category/{category_name}")
def get_by_category(category_name: str):
    result = [p for p in products if p["category"].lower() == category_name.lower()]
    
    if not result:
        return {"error": "No products found in this category"}
    
    return {"products": result}
#Q3
@app.get("/products/instock")
def get_instock():
    instock = [p for p in products if p["in_stock"] == True]
    
    return {
        "in_stock_products": instock,
        "count": len(instock)
    }
#Q4
@app.get("/store/summary")
def store_summary():
    total = len(products)
    instock = len([p for p in products if p["in_stock"]])
    outstock = total - instock
    categories = list(set([p["category"] for p in products]))

    return {
        "store_name": "My E-commerce Store",
        "total_products": total,
        "in_stock": instock,
        "out_of_stock": outstock,
        "categories": categories
    }
# Q5
@app.get("/products/search/{keyword}")
def search_products(keyword: str):
    result = [p for p in products if keyword.lower() in p["name"].lower()]
    
    if not result:
        return {"message": "No products matched your search"}
    
    return {
        "matched_products": result,
        "total_matches": len(result)
    }

# BONUS
@app.get("/products/deals")
def best_deals():
    cheapest = min(products, key=lambda x: x["price"])
    expensive = max(products, key=lambda x: x["price"])

    return {
        "best_deal": cheapest,
        "premium_pick": expensive
    }
#assignment 2
@app.get("/products/filter")
def filter_products(category: str = None, max_price: int = None, min_price: int = None):

    filtered = products

    if category:
        filtered = [p for p in filtered if p["category"].lower() == category.lower()]

    if max_price:
        filtered = [p for p in filtered if p["price"] <= max_price]

    if min_price:
        filtered = [p for p in filtered if p["price"] >= min_price]

    return filtered
#Q2
@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):

    for product in products:
        if product["id"] == product_id:
            return {
                "name": product["name"],
                "price": product["price"]
            }

    return {"error": "Product not found"}
#Q3
@app.post("/feedback")
def submit_feedback(data: CustomerFeedback):

    feedback.append(data.dict())

    return {
        "message": "Feedback submitted successfully",
        "feedback": data,
        "total_feedback": len(feedback)
    }
@app.get("/products/summary")
def product_summary():

    total_products = len(products)

    in_stock = [p for p in products if p["in_stock"]]
    out_stock = [p for p in products if not p["in_stock"]]

    most_expensive = max(products, key=lambda x: x["price"])
    cheapest = min(products, key=lambda x: x["price"])

    categories = list(set([p["category"] for p in products]))

    return {
        "total_products": total_products,
        "in_stock_count": len(in_stock),
        "out_of_stock_count": len(out_stock),
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
#Q4
@app.get("/products/summary")
def products_summary():

    total_products = len(products)

    in_stock = [p for p in products if p["in_stock"]]
    out_of_stock = [p for p in products if not p["in_stock"]]

    most_expensive = max(products, key=lambda x: x["price"])
    cheapest = min(products, key=lambda x: x["price"])

    categories = list(set([p["category"] for p in products]))

    return {
        "total_products": total_products,
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
#Q5
@app.post("/orders/bulk")
def place_bulk_order(order: BulkOrder):
    confirmed, failed, grand_total = [], [], 0
    for item in order.items:
        product = next((p for p in products if p["id"] == item.product_id), None)
        if not product:
            failed.append({"product_id": item.product_id, "reason": "Product not found"})
        elif not product["in_stock"]:
            failed.append({"product_id": item.product_id, "reason": f"{product['name']} is out of stock"})
        else:
            subtotal = product["price"] * item.quantity
            grand_total += subtotal
            confirmed.append({"product": product["name"], "qty": item.quantity, "subtotal": subtotal})
    return {"company": order.company_name, "confirmed": confirmed,
            "failed": failed, "grand_total": grand_total}
@app.post("/orders/bulk")
def bulk_order(order: BulkOrder):

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
                "reason": f'{product["name"]} is out of stock'
            })
            continue

        subtotal = product["price"] * item.quantity
        grand_total += subtotal

        confirmed.append({
            "product": product["name"],
            "qty": item.quantity,
            "subtotal": subtotal
        })

    return {
        "company": order.company_name,
        "confirmed": confirmed,
        "failed": failed,
        "grand_total": grand_total
    }
#BONUS
@app.post("/orders")
def create_order(order: Order):

    global order_counter

    new_order = {
        "order_id": order_counter,
        "product_id": order.product_id,
        "quantity": order.quantity,
        "status": "pending"
    }

    orders.append(new_order)
    order_counter += 1

    return new_order
@app.get("/orders/{order_id}")
def get_order(order_id: int):

    for order in orders:
        if order["order_id"] == order_id:
            return order

    return {"error": "Order not found"}
@app.patch("/orders/{order_id}/confirm")
def confirm_order(order_id: int):

    for order in orders:
        if order["order_id"] == order_id:
            order["status"] = "confirmed"
            return order

    return {"error": "Order not found"}