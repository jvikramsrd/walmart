import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import datetime
import folium
from streamlit_folium import folium_static
import io
import base64

def display_kpi_metrics(kpi_data):
    """Display KPI metrics in a row of 3-4 metric cards"""
    col1, col2, col3, col4 = st.columns(4)
    
    if 'orders_today' in kpi_data:
        col1.metric("Orders Today", kpi_data['orders_today'], kpi_data.get('orders_delta', ""))
    
    if 'inventory_items' in kpi_data:
        col2.metric("Inventory Items", kpi_data['inventory_items'], kpi_data.get('inventory_delta', ""))
    
    if 'low_stock' in kpi_data:
        col3.metric("Low Stock Alerts", kpi_data['low_stock'], kpi_data.get('low_stock_delta', ""), delta_color="inverse")
    
    if 'deliveries_pending' in kpi_data:
        col4.metric("Pending Deliveries", kpi_data['deliveries_pending'], kpi_data.get('deliveries_delta', ""))

def display_custom_metrics(metrics_data):
    """Display custom metrics with icons and styling"""
    cols = st.columns(len(metrics_data))
    
    for i, (metric, data) in enumerate(metrics_data.items()):
        icon = data.get('icon', '📊')
        value = data.get('value', 0)
        delta = data.get('delta', "")
        color = data.get('color', "#0071ce")
        
        # Create custom HTML for metric
        cols[i].markdown(f"""
        <div style="padding: 10px; background-color: #f8f9fa; border-radius: 5px; text-align: center;">
            <div style="font-size: 28px; color: {color};">{icon}</div>
            <div style="font-size: 24px; font-weight: bold;">{value}</div>
            <div style="color: #666;">{metric}</div>
            <div style="color: {'green' if delta.startswith('+') else 'red' if delta.startswith('-') else '#666'}; font-size: 12px;">{delta}</div>
        </div>
        """, unsafe_allow_html=True)

def plot_category_pie_chart(data, title="Category Distribution", custom_colors=None):
    """Generate pie chart for category distribution"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    categories = data['category'].value_counts()
    
    # Use custom colors if provided
    if custom_colors and len(custom_colors) >= len(categories):
        colors = custom_colors[:len(categories)]
    else:
        colors = plt.cm.tab20.colors[:len(categories)]
    
    ax.pie(categories.values, labels=categories.index, autopct='%1.1f%%', 
           shadow=True, startangle=90, colors=colors)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    
    plt.title(title)
    return fig

def plot_bar_chart(data, x_col, y_col, title="", xlabel="", ylabel=""):
    """Generate bar chart from DataFrame columns"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    data.plot(kind='bar', x=x_col, y=y_col, ax=ax, color='#0071ce')
    
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    return fig

def format_date(date_str):
    """Format date string to YYYY-MM-DD format"""
    if not date_str:
        return ""
        
    try:
        # Handle both string and datetime objects
        if isinstance(date_str, datetime.datetime):
            date_obj = date_str
        else:
            date_str = str(date_str).replace('Z', '+00:00')
            date_obj = datetime.datetime.fromisoformat(date_str)
        
        return date_obj.strftime("%Y-%m-%d")
    except:
        return str(date_str)

def format_currency(value):
    """Format value as currency"""
    if value is None:
        return "$0.00"
    try:
        return f"${float(value):,.2f}"
    except:
        return str(value)

def create_download_link(df, filename="data.csv", link_text="Download data as CSV"):
    """Create a download link for a DataFrame"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{link_text}</a>'
    return href

def show_notification(message, type="info"):
    """Show a notification message with the specified type"""
    if type == "success":
        st.success(message)
    elif type == "error":
        st.error(message)
    elif type == "warning":
        st.warning(message)
    else:
        st.info(message)

def create_map(locations, center=None, zoom_start=12):
    """Create a folium map with markers at the specified locations"""
    # Calculate center if not provided
    if not center and locations:
        center_lat = sum(loc[0] for loc in locations) / len(locations)
        center_lng = sum(loc[1] for loc in locations) / len(locations)
        center = [center_lat, center_lng]
    else:
        # Default center (US)
        center = [37.0902, -95.7129]
    
    # Create map
    m = folium.Map(location=center, zoom_start=zoom_start)
    
    # Add markers
    for i, location in enumerate(locations):
        popup_text = f"Location {i+1}"
        if isinstance(location, dict) and 'popup' in location:
            popup_text = location['popup']
            location = location['position']
            
        icon_color = 'blue'
        if isinstance(location, dict) and 'color' in location:
            icon_color = location['color']
            location = location['position']
            
        folium.Marker(
            location=location,
            popup=popup_text,
            icon=folium.Icon(color=icon_color)
        ).add_to(m)
    
    return m

def display_map(m):
    """Display a folium map in Streamlit"""
    folium_static(m)
    
def get_color_for_value(value, min_val, max_val, palette='viridis'):
    """Get color from a palette based on normalized value"""
    if min_val == max_val:
        norm_value = 0.5
    else:
        norm_value = (value - min_val) / (max_val - min_val)
    
    cmap = plt.get_cmap(palette)
    return mcolors.rgb2hex(cmap(norm_value))

def filter_dataframe(df, filters):
    """Filter a DataFrame based on a dictionary of filters"""
    filtered_df = df.copy()
    
    for column, value in filters.items():
        if column in filtered_df.columns:
            if value is not None:
                if isinstance(value, list):
                    if value:  # Only apply if list is not empty
                        filtered_df = filtered_df[filtered_df[column].isin(value)]
                elif isinstance(value, tuple) and len(value) == 2:
                    # Range filter for dates or numbers
                    start, end = value
                    if start and end:
                        filtered_df = filtered_df[(filtered_df[column] >= start) & 
                                                (filtered_df[column] <= end)]
                else:
                    # Exact match or string contains
                    if isinstance(filtered_df[column].dtype, pd.StringDtype) or filtered_df[column].dtype == 'object':
                        filtered_df = filtered_df[filtered_df[column].str.contains(str(value), case=False, na=False)]
                    else:
                        filtered_df = filtered_df[filtered_df[column] == value]
    
    return filtered_df

def optimize_route(addresses):
    """Simulated route optimization function"""
    # This is a placeholder for an actual route optimization algorithm
    # For a real implementation, you would call an external service or algorithm
    
    # Simulate route order (no actual optimization)
    route = [(i + 1, addr) for i, addr in enumerate(addresses)]
    
    # Placeholder for actual distance calculation
    total_distance = len(addresses) * 5  # 5 miles per stop on average
    
    # Estimate time based on distance (30 mph average)
    total_time = total_distance / 30
    
    return {
        "route": route,
        "total_distance": total_distance,
        "total_time": total_time,
        "co2_emissions": total_distance * 0.12  # 0.12 kg CO2 per mile
    }
