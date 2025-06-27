from pymongo import MongoClient
import os

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "walmart")
client = MongoClient(MONGODB_URI)
db = client[MONGODB_DB]

# Sample Orders
db.orders.delete_many({})  # Clear existing
orders = [
    {
        "order_id": "ORD-1001",
        "customer_name": "Alice Smith",
        "product_id": "SKU-2001",
        "quantity": 2,
        "delivery_address": "123 Main St, Springfield",
        "status": "pending",
        "order_date": "2024-06-25T10:30:00"
    },
    {
        "order_id": "ORD-1002",
        "customer_name": "Bob Johnson",
        "product_id": "SKU-2002",
        "quantity": 1,
        "delivery_address": "456 Oak Ave, Metropolis",
        "status": "shipped",
        "order_date": "2024-06-24T14:15:00"
    },
    {
        "order_id": "ORD-1003",
        "customer_name": "Carol Lee",
        "product_id": "SKU-2003",
        "quantity": 3,
        "delivery_address": "789 Pine Rd, Gotham",
        "status": "delivered",
        "order_date": "2024-06-23T09:00:00"
    }
]
db.orders.insert_many(orders)

# Sample Inventory
db.inventory.delete_many({})
inventory = [
    {
        "sku": "SKU-2001",
        "name": "Laptop",
        "category": "Electronics",
        "quantity": 10,
        "bin_location": "A1",
        "min_stock_level": 3
    },
    {
        "sku": "SKU-2002",
        "name": "Wireless Mouse",
        "category": "Electronics",
        "quantity": 5,
        "bin_location": "B2",
        "min_stock_level": 2
    },
    {
        "sku": "SKU-2003",
        "name": "Office Chair",
        "category": "Furniture",
        "quantity": 2,
        "bin_location": "C3",
        "min_stock_level": 5
    }
]
db.inventory.insert_many(inventory)

# Sample Deliveries
db.deliveries.delete_many({})
deliveries = [
    {
        "delivery_id": "DEL-5001",
        "agent_id": "AG-01",
        "region": "North",
        "status": "in-transit",
        "delivery_date": "2024-06-25T12:00:00",
        "eta": "2024-06-25T14:00:00",
        "latitude": 40.7128,
        "longitude": -74.0060
    },
    {
        "delivery_id": "DEL-5002",
        "agent_id": "AG-02",
        "region": "South",
        "status": "delivered",
        "delivery_date": "2024-06-24T10:00:00",
        "eta": "2024-06-24T12:00:00",
        "latitude": 34.0522,
        "longitude": -118.2437
    },
    {
        "delivery_id": "DEL-5003",
        "agent_id": "AG-03",
        "region": "East",
        "status": "failed",
        "delivery_date": "2024-06-23T09:00:00",
        "eta": "2024-06-23T11:00:00",
        "latitude": 41.8781,
        "longitude": -87.6298
    }
]
db.deliveries.insert_many(deliveries)

# Sample Warehouse
db.warehouse.delete_many({})
warehouse = {
    "name": "Main Warehouse",
    "address": "123 Main St, City",
    "capacity": 1000,
    "manager": "John Doe",
    "contact": "555-1234"
}
db.warehouse.insert_one(warehouse)

print("Sample data inserted into orders, inventory, deliveries, and warehouse collections.") 