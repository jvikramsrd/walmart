import requests
import streamlit as st
import json
import os
import datetime
import time
import random
import math
from functools import wraps

# API Configuration
API_BASE = "http://localhost:3000/api"
USE_MOCK_DATA = False  # Set to False when real API is available
MOCK_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mock_data")

# Create mock data directory if it doesn't exist
if not os.path.exists(MOCK_DATA_DIR):
    os.makedirs(MOCK_DATA_DIR)

# Cache decorator to minimize API calls
def cache_response(ttl_seconds=300):
    """Cache decorator with time-to-live (TTL) in seconds"""
    def decorator(func):
        cache = {}
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = str(args) + str(kwargs)
            current_time = time.time()
            if key in cache:
                result, timestamp = cache[key]
                if current_time - timestamp < ttl_seconds:
                    return result
            result = func(*args, **kwargs)
            cache[key] = (result, current_time)
            return result
        return wrapper
    return decorator

def generate_mock_data(endpoint):
    """Generate mock data for different API endpoints"""
    if endpoint == "orders" or endpoint.startswith("orders/"):
        return generate_mock_orders()
    elif endpoint == "inventory" or endpoint.startswith("inventory/"):
        return generate_mock_inventory()
    elif endpoint == "deliveries" or endpoint.startswith("deliveries/"):
        return generate_mock_deliveries()
    elif endpoint == "warehouse" or endpoint.startswith("warehouse/"):
        return generate_mock_warehouse()
    elif endpoint.startswith("optimize_route"):
        return generate_mock_route_optimization()
    else:
        return []

def save_mock_data(endpoint, data):
    """Save mock data to file"""
    filename = f"{endpoint.replace('/', '_')}.json"
    filepath = os.path.join(MOCK_DATA_DIR, filename)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def load_mock_data(endpoint):
    """Load mock data from file"""
    filename = f"{endpoint.replace('/', '_')}.json"
    filepath = os.path.join(MOCK_DATA_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return None

@cache_response(ttl_seconds=60)
def get_data(endpoint):
    """Get data from API with error handling and mock data fallback"""
    if USE_MOCK_DATA:
        # Try to load existing mock data
        mock_data = load_mock_data(endpoint)
        if mock_data:
            return mock_data
        
        # Generate and save new mock data
        mock_data = generate_mock_data(endpoint)
        if mock_data:
            save_mock_data(endpoint, mock_data)
            return mock_data
    
    # Real API request
    try:
        response = requests.get(f"{API_BASE}/{endpoint}", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return []

def post_data(endpoint, payload):
    """Post data to API with error handling and mock data support"""
    if USE_MOCK_DATA:
        # Load existing mock data
        mock_data = load_mock_data(endpoint.split('/')[0])
        if not mock_data:
            mock_data = generate_mock_data(endpoint.split('/')[0])
        
        # Add ID to payload if needed
        if isinstance(mock_data, list):
            if 'id' not in payload:
                max_id = max([item.get('id', 0) for item in mock_data]) if mock_data else 0
                payload['id'] = max_id + 1
            mock_data.append(payload)
        elif isinstance(mock_data, dict):
            # Handle specific dictionary structures based on endpoint
            pass
        
        # Save updated mock data
        save_mock_data(endpoint.split('/')[0], mock_data)
        return True, payload
    
    # Real API request
    try:
        response = requests.post(f"{API_BASE}/{endpoint}", json=payload, timeout=10)
        if response.status_code in (200, 201):
            return True, response.json() if response.text else payload
        else:
            st.warning(f"API returned status code: {response.status_code}")
            return False, None
    except Exception as e:
        st.error(f"Error submitting data: {str(e)}")
        return False, None
        
def put_data(endpoint, payload):
    """Update data via API with error handling and mock data support"""
    if USE_MOCK_DATA:
        # Get ID from endpoint
        parts = endpoint.split('/')
        resource_type = parts[0]
        resource_id = parts[1] if len(parts) > 1 else None
        
        # Load existing mock data
        mock_data = load_mock_data(resource_type)
        if not mock_data:
            mock_data = generate_mock_data(resource_type)
        
        # Update the item
        if isinstance(mock_data, list) and resource_id:
            for i, item in enumerate(mock_data):
                if str(item.get('id')) == str(resource_id):
                    mock_data[i] = {**item, **payload}
                    save_mock_data(resource_type, mock_data)
                    return True, mock_data[i]
        
        return False, None
    
    # Real API request
    try:
        response = requests.put(f"{API_BASE}/{endpoint}", json=payload, timeout=10)
        if response.status_code == 200:
            return True, response.json() if response.text else payload
        else:
            st.warning(f"API returned status code: {response.status_code}")
            return False, None
    except Exception as e:
        st.error(f"Error updating data: {str(e)}")
        return False, None
        
def delete_data(endpoint):
    """Delete data via API with error handling and mock data support"""
    if USE_MOCK_DATA:
        # Get ID from endpoint
        parts = endpoint.split('/')
        resource_type = parts[0]
        resource_id = parts[1] if len(parts) > 1 else None
        
        # Load existing mock data
        mock_data = load_mock_data(resource_type)
        if not mock_data:
            return True  # Nothing to delete
        
        # Delete the item
        if isinstance(mock_data, list) and resource_id:
            mock_data = [item for item in mock_data if str(item.get('id')) != str(resource_id)]
            save_mock_data(resource_type, mock_data)
        
        return True
    
    # Real API request
    try:
        response = requests.delete(f"{API_BASE}/{endpoint}", timeout=10)
        return response.status_code in (200, 204)
    except Exception as e:
        st.error(f"Error deleting data: {str(e)}")
        return False

# Mock data generation functions
def generate_mock_orders(count=20):
    """Generate mock order data"""
    orders = []
    statuses = ["pending", "shipped", "delivered", "cancelled"]
    products = ["Laptop", "Smartphone", "Tablet", "Headphones", "Monitor", "Keyboard", "Mouse", "Printer", "Speaker", "Camera"]
    
    for i in range(1, count + 1):
        # Calculate a random date within the last 30 days
        days_ago = random.randint(0, 30)
        order_date = (datetime.datetime.now() - datetime.timedelta(days=days_ago)).isoformat()
        
        # Generate a random order
        order = {
            "id": i,
            "order_id": f"ORD-{2023000 + i}",
            "customer_name": f"Customer {i}",
            "customer_email": f"customer{i}@example.com",
            "product_id": f"PROD-{random.randint(1000, 9999)}",
            "product_name": random.choice(products),
            "quantity": random.randint(1, 5),
            "price": round(random.uniform(50, 1000), 2),
            "status": random.choice(statuses),
            "order_date": order_date,
            "delivery_address": f"{random.randint(1, 999)} Main St, City {i}, State",
            "payment_method": random.choice(["Credit Card", "PayPal", "Cash on Delivery"])
        }
        orders.append(order)
    
    return orders

def generate_mock_inventory(count=30):
    """Generate mock inventory data"""
    inventory = []
    categories = ["Electronics", "Clothing", "Groceries", "Home Goods", "Sports", "Toys", "Health", "Beauty"]
    
    for i in range(1, count + 1):
        # Generate random inventory item
        min_stock = random.randint(5, 20)
        quantity = random.randint(0, 40)
        
        item = {
            "id": i,
            "sku": f"SKU-{10000 + i}",
            "name": f"Product {i}",
            "description": f"Description for Product {i}",
            "category": random.choice(categories),
            "quantity": quantity,
            "price": round(random.uniform(10, 500), 2),
            "bin_location": f"{random.choice('ABCDE')}{random.randint(1, 20)}",
            "min_stock_level": min_stock,
            "last_restocked": (datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 60))).isoformat(),
            "supplier": f"Supplier {random.randint(1, 10)}"
        }
        inventory.append(item)
    
    return inventory

def generate_mock_deliveries(count=15):
    """Generate mock delivery data"""
    deliveries = []
    statuses = ["pending", "in-transit", "delivered", "failed", "rescheduled"]
    
    for i in range(1, count + 1):
        # Calculate a random delivery date within the next 7 days
        days_ahead = random.randint(-2, 7)  # Include some in the past
        delivery_date = (datetime.datetime.now() + datetime.timedelta(days=days_ahead)).isoformat()
        
        # Random delivery time
        hours_ahead = random.randint(1, 8)
        eta = (datetime.datetime.now() + datetime.timedelta(hours=hours_ahead)).isoformat()
        
        # Random coordinates in a reasonable US range
        latitude = round(random.uniform(30, 45), 6)
        longitude = round(random.uniform(-85, -120), 6)
        
        delivery = {
            "id": i,
            "delivery_id": f"DEL-{30000 + i}",
            "order_id": f"ORD-{2023000 + random.randint(1, 20)}",
            "agent_id": f"DRV-{100 + random.randint(1, 10)}",
            "agent_name": f"Driver {random.randint(1, 10)}",
            "status": random.choice(statuses),
            "delivery_date": delivery_date,
            "eta": eta,
            "region": random.choice(["North", "South", "East", "West", "Central"]),
            "latitude": latitude,
            "longitude": longitude,
            "address": f"{random.randint(1, 999)} Main St, City {i}, State",
            "notes": "Leave at door" if random.random() > 0.5 else ""
        }
        deliveries.append(delivery)
    
    return deliveries

def generate_mock_warehouse():
    """Generate mock warehouse data including bins and activity"""
    # Create warehouse layout
    rows = 10
    cols = 15
    bins = []
    
    for row in range(rows):
        for col in range(cols):
            # Skip some positions to create aisles
            if col % 5 == 0 and col > 0:  # Create vertical aisles
                continue
                
            # Determine bin status
            status_weights = {"occupied": 0.7, "empty": 0.2, "reserved": 0.05, "damaged": 0.05}
            status = random.choices(
                list(status_weights.keys()),
                weights=list(status_weights.values()),
                k=1
            )[0]
            
            bin_data = {
                "bin_id": f"{chr(65 + row)}{col+1}",
                "row": row,
                "col": col,
                "status": status,
                "content": f"SKU-{10000 + random.randint(1, 30)}" if status == "occupied" else None
            }
            bins.append(bin_data)
    
    # Create activity data for heatmap
    activity = []
    
    for row in range(rows):
        for col in range(cols):
            # Skip aisle positions
            if col % 5 == 0 and col > 0:
                continue
                
            # Higher activity near entrance (0,0) and popular aisles
            distance_from_entrance = row + col
            base_activity = max(10 - (distance_from_entrance / 2), 1)
            
            # Add randomness
            activity_level = base_activity + random.uniform(-1, 5)
            # Ensure it's positive
            activity_level = max(0.1, activity_level)
            
            activity_data = {
                "row": row,
                "col": col,
                "activity_level": round(activity_level, 2)
            }
            activity.append(activity_data)
    
    return {
        "bins": bins,
        "activity": activity,
        "layout": {
            "rows": rows,
            "cols": cols
        }
    }

def generate_mock_route_optimization():
    """Generate mock route optimization data"""
    # Create random coordinates in a city-like grid
    num_stops = random.randint(5, 10)
    center_lat = 37.7749  # Example: San Francisco
    center_lng = -122.4194
    
    # Generate route coordinates
    coordinates = []
    for i in range(num_stops):
        # Create points in a rough circle
        angle = (i / num_stops) * 2 * 3.14159
        radius = random.uniform(0.01, 0.05)
        lat = center_lat + radius * math.sin(angle)
        lng = center_lng + radius * math.cos(angle)
        coordinates.append([round(lat, 6), round(lng, 6)])
    
    # Start from a random point
    start_idx = random.randint(0, num_stops - 1)
    coordinates = coordinates[start_idx:] + coordinates[:start_idx]
    
    # Create route details
    route_details = []
    total_distance = 0
    for i, coord in enumerate(coordinates):
        stop = {
            "stop_number": i + 1,
            "address": f"Stop {i+1}",
            "coordinates": coord
        }
        route_details.append(stop)
        
        if i > 0:
            # Calculate rough distance from previous stop
            prev = coordinates[i-1]
            dist = math.sqrt((coord[0] - prev[0])**2 + (coord[1] - prev[1])**2) * 111  # rough km conversion
            total_distance += dist
    
    # Generate clusters for multi-vehicle routing
    clusters = {}
    if num_stops > 4:
        num_clusters = min(3, num_stops // 2)
        stops_per_cluster = num_stops // num_clusters
        
        for c in range(num_clusters):
            start_idx = c * stops_per_cluster
            end_idx = start_idx + stops_per_cluster if c < num_clusters - 1 else num_stops
            
            cluster_points = coordinates[start_idx:end_idx]
            # Calculate centroid
            centroid = [
                sum(p[0] for p in cluster_points) / len(cluster_points),
                sum(p[1] for p in cluster_points) / len(cluster_points)
            ]
            
            clusters[str(c+1)] = {
                "points": cluster_points,
                "centroid": centroid,
                "num_stops": len(cluster_points)
            }
    
    return {
        "route": route_details,
        "coordinates": coordinates,
        "total_distance": round(total_distance, 1),
        "total_time": round(total_distance / 40, 1),  # Rough estimate: 40 km/h
        "co2_emissions": round(total_distance * 0.12, 1),  # Rough estimate: 0.12 kg/km
        "clusters": clusters
    }
    