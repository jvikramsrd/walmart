from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "walmart")

client = MongoClient(MONGODB_URI)
db = client[MONGODB_DB]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def serialize_doc(doc):
    doc["_id"] = str(doc["_id"])
    return doc

# Orders Endpoints
@app.get("/api/orders")
def get_orders():
    return [serialize_doc(order) for order in db.orders.find()]

@app.post("/api/orders")
def add_order(order: dict):
    result = db.orders.insert_one(order)
    order["_id"] = str(result.inserted_id)
    return {"success": True, "order": order}

@app.put("/api/orders/{order_id}")
def update_order(order_id: str, order: dict):
    result = db.orders.update_one({"_id": ObjectId(order_id)}, {"$set": order})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"success": True}

@app.delete("/api/orders/{order_id}")
def delete_order(order_id: str):
    result = db.orders.delete_one({"_id": ObjectId(order_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"success": True}

# Inventory Endpoints
@app.get("/api/inventory")
def get_inventory():
    return [serialize_doc(item) for item in db.inventory.find()]

@app.post("/api/inventory")
def add_inventory(item: dict):
    result = db.inventory.insert_one(item)
    item["_id"] = str(result.inserted_id)
    return {"success": True, "item": item}

@app.put("/api/inventory/{sku}")
def update_inventory(sku: str, item: dict):
    result = db.inventory.update_one({"sku": sku}, {"$set": item})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="SKU not found")
    return {"success": True}

@app.delete("/api/inventory/{sku}")
def delete_inventory(sku: str):
    result = db.inventory.delete_one({"sku": sku})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="SKU not found")
    return {"success": True}

# Deliveries Endpoints
@app.get("/api/deliveries")
def get_deliveries():
    return [serialize_doc(delivery) for delivery in db.deliveries.find()]

@app.post("/api/deliveries")
def add_delivery(delivery: dict):
    result = db.deliveries.insert_one(delivery)
    delivery["_id"] = str(result.inserted_id)
    return {"success": True, "delivery": delivery}

@app.put("/api/deliveries/{delivery_id}")
def update_delivery(delivery_id: str, delivery: dict):
    result = db.deliveries.update_one({"_id": ObjectId(delivery_id)}, {"$set": delivery})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return {"success": True}

@app.delete("/api/deliveries/{delivery_id}")
def delete_delivery(delivery_id: str):
    result = db.deliveries.delete_one({"_id": ObjectId(delivery_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return {"success": True}

# Warehouse Endpoints
@app.get("/api/warehouse")
def get_warehouse():
    warehouse = db.warehouse.find_one()
    if warehouse:
        return serialize_doc(warehouse)
    return {}

@app.post("/api/warehouse")
def add_warehouse(warehouse: dict):
    result = db.warehouse.insert_one(warehouse)
    warehouse["_id"] = str(result.inserted_id)
    return {"success": True, "warehouse": warehouse}

@app.put("/api/warehouse/{warehouse_id}")
def update_warehouse(warehouse_id: str, warehouse: dict):
    result = db.warehouse.update_one({"_id": ObjectId(warehouse_id)}, {"$set": warehouse})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return {"success": True}

# Optimizer Endpoint (stub)
@app.post("/api/optimize_route")
def optimize_route(payload: dict):
    addresses = payload.get("addresses", [])
    # Dummy route: just return the addresses in order, with fake metrics
    route = [(i + 1, addr) for i, addr in enumerate(addresses)]
    total_distance = len(addresses) * 5
    total_time = total_distance / 30
    co2_emissions = total_distance * 0.12
    # Optionally, add fake coordinates for map
    coordinates = [[40.0 + i * 0.01, -74.0 + i * 0.01] for i in range(len(addresses))]
    return {
        "route": route,
        "total_distance": total_distance,
        "total_time": total_time,
        "co2_emissions": co2_emissions,
        "coordinates": coordinates
    }

# TODO: Add endpoints for warehouse, delivery, optimizer as needed. 