import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from utils.api import get_data

@st.cache_data(ttl=10)
def fetch_warehouse():
    return get_data("warehouse")

@st.cache_data(ttl=10)
def fetch_inventory():
    return get_data("inventory")

def app():
    """
    Renders the Warehouse Management page.
    """
    st.header("Warehouse Management")

    warehouse_data = fetch_warehouse()
    inventory_data = fetch_inventory()

    if warehouse_data is None or inventory_data is None:
        st.warning("Could not fetch warehouse or inventory data. The backend might be down.")
        return
        
    # Since the new API returns a list of warehouses, we'll take the first one.
    warehouse = warehouse_data[0] if warehouse_data else {}

    # --- KPIs ---
    st.subheader("Key Metrics")
    if warehouse and "capacity" in warehouse:
        inventory_df = pd.DataFrame(inventory_data)
        total_items = inventory_df['quantity'].sum()
        capacity = warehouse.get('capacity', 0)
        utilization = (total_items / capacity * 100) if capacity > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        col1.metric("📦 Total Items", f"{total_items:,}")
        col2.metric("🏢 Warehouse Capacity", f"{capacity:,}")
        col3.metric("📈 Utilization", f"{utilization:.2f}%")
    else:
        st.info("No warehouse data available to display KPIs.")

    st.markdown("---")

    tab1, tab2 = st.tabs(["Warehouse Details", "Inventory Heatmap"])

    with tab1:
        st.subheader("Warehouse Information")
        if warehouse:
            st.text(f"Name: {warehouse.get('name', 'N/A')}")
            st.text(f"Address: {warehouse.get('address', 'N/A')}")
            st.text(f"Manager: {warehouse.get('manager', 'N/A')}")
            st.text(f"Contact: {warehouse.get('contact', 'N/A')}")
        else:
            st.info("No warehouse details to display.")
    
    with tab2:
        st.subheader("Inventory Location Heatmap")
        if not pd.DataFrame(inventory_data).empty:
            df_inv = pd.DataFrame(inventory_data)
            # Assuming bin_location is in a 'A1', 'B12' format
            df_inv['row'] = (
                df_inv['bin_location']
                .str.extract(r'([A-Z])')[0]
                .fillna('A')
                .apply(lambda x: ord(x) - ord('A'))
            )
            df_inv['col'] = (
                df_inv['bin_location']
                .str.extract(r'(\d+)')[0]
                .fillna(0)
                .astype(int)
            )

            if not df_inv.empty and 'row' in df_inv.columns and 'col' in df_inv.columns:
                max_row = df_inv['row'].max()
                max_col = df_inv['col'].max()
                
                heatmap_grid = np.zeros((max_row + 1, max_col + 1))
                
                for _, item in df_inv.iterrows():
                    heatmap_grid[item['row'], item['col']] = item['quantity']
                
                fig, ax = plt.subplots(figsize=(12, 8))
                heatmap = ax.imshow(heatmap_grid, cmap='hot', interpolation='nearest')
                plt.colorbar(heatmap, ax=ax, label='Item Quantity')
                ax.set_title("Warehouse Inventory Heatmap")
                st.pyplot(fig)
            else:
                st.info("Could not generate heatmap due to missing location data.")
        else:
            st.info("No inventory data for heatmap.")

    st.markdown("---")
    # Add form can be added here if needed
    # with st.expander("Add New Warehouse"): ...
