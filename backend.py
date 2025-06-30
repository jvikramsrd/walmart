import os
import datetime
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
from typing import List, Optional

# --- Environment and DB Setup ---
load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "walmart")
SECRET_KEY = os.getenv("SECRET_KEY", "a_very_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

client = MongoClient(MONGODB_URI)
db = client[MONGODB_DB]

app = FastAPI(title="Walmart Logistics API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---
class Order(BaseModel):
    order_id: str
    customer_name: str
    product_id: str
    quantity: int
    delivery_address: str
    status: str
    order_date: str

class InventoryItem(BaseModel):
    sku: str
    name: str
    category: str
    quantity: int
    bin_location: str
    min_stock_level: int

class Delivery(BaseModel):
    delivery_id: str
    agent_id: str
    region: str
    status: str
    delivery_date: str
    eta: str
    latitude: float
    longitude: float

class Warehouse(BaseModel):
    name: str
    address: str
    capacity: int
    manager: str
    contact: str

class User(BaseModel):
    username: str
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# --- Auth Setup ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

# --- Auth Helpers ---
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(username: str):
    user = db.users.find_one({"username": username})
    if user:
        return UserInDB(**user)
    return None

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + (expires_delta or datetime.timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# --- Auth Endpoints ---
@app.post("/api/login", response_model=Token, tags=["Authentication"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# --- Utility ---
def serialize_doc(doc):
    doc["_id"] = str(doc["_id"])
    return doc

# --- Orders Endpoints ---
@app.get("/api/orders", response_model=List[Order], tags=["Orders"])
async def get_orders():
    return [order for order in db.orders.find()]

@app.post("/api/orders", response_model=Order, status_code=201, tags=["Orders"])
async def add_order(order: Order):
    order_dict = order.dict()
    db.orders.insert_one(order_dict)
    return order

@app.patch("/api/orders/{order_id}", status_code=204, tags=["Orders"])
async def patch_order(order_id: str, patch: dict):
    if "status" in patch:
        patch["status"] = patch["status"].lower()
    result = db.orders.update_one({"order_id": order_id}, {"$set": patch})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    return

@app.delete("/api/orders/{order_id}", status_code=204, tags=["Orders"])
async def delete_order(order_id: str):
    result = db.orders.delete_one({"order_id": order_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    return

# --- Inventory Endpoints ---
@app.get("/api/inventory", response_model=List[InventoryItem], tags=["Inventory"])
async def get_inventory():
    return [item for item in db.inventory.find()]

@app.post("/api/inventory", response_model=InventoryItem, status_code=201, tags=["Inventory"])
async def add_inventory(item: InventoryItem):
    item_dict = item.dict()
    db.inventory.insert_one(item_dict)
    return item

@app.patch("/api/inventory/{sku}", status_code=204, tags=["Inventory"])
async def patch_inventory(sku: str, patch: dict):
    result = db.inventory.update_one({"sku": sku}, {"$set": patch})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="SKU not found")
    return

@app.delete("/api/inventory/{sku}", status_code=204, tags=["Inventory"])
async def delete_inventory(sku: str):
    result = db.inventory.delete_one({"sku": sku})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="SKU not found")
    return

# --- Deliveries Endpoints ---
@app.get("/api/deliveries", response_model=List[Delivery], tags=["Deliveries"])
async def get_deliveries():
    return [delivery for delivery in db.deliveries.find()]

@app.post("/api/deliveries", response_model=Delivery, status_code=201, tags=["Deliveries"])
async def add_delivery(delivery: Delivery):
    delivery_dict = delivery.dict()
    db.deliveries.insert_one(delivery_dict)
    return delivery

@app.patch("/api/deliveries/{delivery_id}", status_code=204, tags=["Deliveries"])
async def patch_delivery(delivery_id: str, patch: dict):
    if "status" in patch:
        patch["status"] = patch["status"].lower()
    result = db.deliveries.update_one({"delivery_id": delivery_id}, {"$set": patch})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return

@app.delete("/api/deliveries/{delivery_id}", status_code=204, tags=["Deliveries"])
async def delete_delivery(delivery_id: str):
    result = db.deliveries.delete_one({"delivery_id": delivery_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return

# --- Warehouse Endpoints ---
@app.get("/api/warehouse", response_model=List[Warehouse], tags=["Warehouse"])
async def get_warehouses():
    return [serialize_doc(w) for w in db.warehouse.find()]

@app.post("/api/warehouse", response_model=Warehouse, status_code=201, tags=["Warehouse"])
async def add_warehouse(warehouse: Warehouse):
    warehouse_dict = warehouse.dict()
    db.warehouse.insert_one(warehouse_dict)
    return warehouse

# --- Optimizer Endpoint ---
@app.post("/api/optimize_route", tags=["Optimizer"])
async def optimize_route(payload: dict):
    addresses = payload.get("addresses", [])
    # Dummy implementation
    route = [(i + 1, addr) for i, addr in enumerate(addresses)]
    return {
        "success": True,
        "route": route,
        "total_distance": len(addresses) * 5,
        "total_time": len(addresses) * 5 / 30,
        "co2_emissions": len(addresses) * 5 * 0.12,
        "coordinates": [[40.0 + i * 0.01, -74.0 + i * 0.01] for i in range(len(addresses))]
    }

# --- Create a default user if none exists ---
if not db.users.find_one({"username": "admin"}):
    db.users.insert_one({
        "username": "admin",
        "full_name": "Administrator",
        "hashed_password": get_password_hash("admin"),
        "disabled": False
    }) 