# Walmart Logistics Dashboard

A comprehensive Streamlit-based dashboard for managing Walmart logistics operations including orders, inventory, delivery tracking, warehouse management, and route optimization.

---

## 🚀 Features

### 🔐 Authentication
- Secure login/logout with JWT-based authentication (default: admin/admin)
- All data-changing actions require login

### 📦 Orders Tab
- View all current orders in a table
- Filter by date, status (pending, shipped, cancelled)
- Cancel orders, mark as dispatched
- Add new orders form
- Real-time KPIs

### 📚 Inventory Tab
- Table of current inventory (SKU, qty, bin)
- Filters by SKU and low stock alerts
- Add new SKUs and update stock
- Category-wise stock pie chart
- Real-time KPIs

### 🚚 Delivery Tab
- Track delivery status
- Reschedule failed deliveries
- Live map tracking and route visualization
- Real-time KPIs

### 🏢 Warehouse Tab
- Warehouse info and capacity metrics
- Inventory heatmap by bin location
- Real-time KPIs

### 🧠 Optimizer Tab
- Input delivery addresses manually or via file upload
- Route optimization with distance and ETA calculations
- Route visualization on map

---

## 🛠️ Getting Started

### Prerequisites
- Python 3.8 or higher
- MongoDB running locally or accessible via URI
- pip (Python package manager)

### Installation

1. **Clone this repository:**
   ```bash
   git clone https://github.com/vedasri2511/walmart.git
   cd walmart
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **(Optional) Populate sample data:**
   ```bash
   python populate_sample_data.py
   ```

4. **Start the backend API:**
   ```bash
   uvicorn backend:app --reload --port 3000
   ```
   - The backend runs at `http://localhost:3000/api` by default.
   - Default admin user: `admin` / `admin`

5. **Start the frontend dashboard:**
   ```bash
   streamlit run app.py
   ```

---

## ⚙️ Backend API
- FastAPI-based, async endpoints
- JWT authentication for all mutating endpoints
- MongoDB for persistent storage
- Endpoints: `/api/orders`, `/api/inventory`, `/api/deliveries`, `/api/warehouse`, `/api/optimize_route`, `/api/login`

---

## 🗂️ File Structure

```
walmart/
├── app.py                 # Main Streamlit app
├── backend.py             # FastAPI backend
├── requirements.txt       # Python dependencies
├── README.md              # Documentation
├── assets/               # Images and logos
├── tabs/                 # Dashboard tabs
│   ├── __init__.py
│   ├── orders.py
│   ├── inventory.py
│   ├── delivery.py
│   ├── warehouse.py
│   ├── optimizer.py
│   └── login.py
├── utils/                # Utility functions
│   ├── __init__.py
│   ├── api.py            # API connections (with error handling & caching)
│   └── helpers.py        # Helper functions
├── populate_sample_data.py # Script to populate MongoDB with sample data
└── mock_data/            # (Optional) Mock data for development
```

---

## 📝 Notes & Improvements
- **Error Handling:** All API errors are now gracefully handled and shown in the UI.
- **Caching:** Data tables use Streamlit caching for smooth, flicker-free updates.
- **Modern UI/UX:** Material-inspired design, responsive layout, and real-time KPIs.
- **Security:** All sensitive actions require authentication.
- **Extensible:** Add new tabs or backend endpoints as needed.

---

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- Streamlit for the awesome framework
- FastAPI for the backend
- Folium for map visualizations
- Matplotlib for charts and visualizations
