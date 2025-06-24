# Walmart Logistics Dashboard

A comprehensive Streamlit-based dashboard for managing Walmart logistics operations including orders, inventory, delivery tracking, warehouse management, and route optimization.

## Features

### 📦 Orders Tab
- View all current orders in a table
- Filter by date, status (pending, shipped, cancelled)
- Refresh, cancel orders, and mark as dispatched
- Add new orders form

### 📚 Inventory Tab
- Table of current inventory (SKU, qty, bin)
- Filters by SKU and low stock alerts
- Add new SKUs and update stock
- Category-wise stock pie chart

### 🚚 Delivery Tab
- Track delivery status
- Filter deliveries by date, agent, and region
- Live map tracking and route visualization
- Rescheduling for failed deliveries

### 🏢 Warehouse Tab
- Grid-style visualization of warehouse bins
- Route simulator with A* algorithm visualization
- Optimize slotting feature
- Heatmap of warehouse busy zones

### 🧠 Optimizer Tab
- Input delivery addresses manually or via file upload
- Route optimization with distance and ETA calculations
- Route visualization on map
- Clustering routes using DBSCAN algorithm

## Getting Started

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone this repository:
```
git clone https://github.com/yourusername/walmart-logistics-dashboard.git
cd walmart-logistics-dashboard
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Run the application:
```
streamlit run app.py
```

## Backend API

The dashboard connects to a backend API that should be running on `http://localhost:3000/api`. Make sure to set up the backend service before running the dashboard.

## File Structure

```
walmart-logistics-dashboard/
├── app.py                 # Main application file
├── requirements.txt       # Python dependencies
├── README.md              # Documentation
├── assets/               
│   └── walmart_logo.png   # Logo image
├── tabs/                  # Dashboard tabs
│   ├── __init__.py
│   ├── orders.py
│   ├── inventory.py
│   ├── delivery.py
│   ├── warehouse.py
│   └── optimizer.py
└── utils/                 # Utility functions
    ├── __init__.py
    ├── api.py             # API connections
    └── helpers.py         # Helper functions
```

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- Streamlit for the awesome framework
- Folium for the map visualizations
- Matplotlib for charts and visualizations
